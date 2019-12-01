# Node definition for a daily forecast node

CLOUD = False
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
    CLOUD = True

import json
import time
import datetime
import et3

LOGGER = polyinterface.LOGGER

class DailyNode(polyinterface.Node):
    id = 'daily'
    # TODO: add wind speed min/max, pop, winddir min/max
    drivers = [
            {'driver': 'GV19', 'value': 0, 'uom': 25},     # day of week
            {'driver': 'GV0', 'value': 0, 'uom': 4},       # high temp
            {'driver': 'GV1', 'value': 0, 'uom': 4},       # low temp
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV11', 'value': 0, 'uom': 25},     # coverage
            {'driver': 'GV12', 'value': 0, 'uom': 25},     # intensity
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # weather
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # clouds
            {'driver': 'GV4', 'value': 0, 'uom': 49},      # wind speed
            {'driver': 'GV5', 'value': 0, 'uom': 49},      # gust speed
            {'driver': 'GV6', 'value': 0, 'uom': 82},      # precipitation
            {'driver': 'GV7', 'value': 0, 'uom': 49},      # wind speed max
            {'driver': 'GV8', 'value': 0, 'uom': 49},      # wind speed min
            {'driver': 'GV18', 'value': 0, 'uom': 22},     # pop
            {'driver': 'GV16', 'value': 0, 'uom': 71},     # UV index
            {'driver': 'GV20', 'value': 0, 'uom': 106},    # mm/day
            ]
    uom = {'GV19': 25,
            'GV0': 4,
            'GV1': 4,
            'CLIHUM': 22,
            'BARPRES': 117,
            'GV11': 25,
            'GV12': 25,
            'GV13': 25,
            'GV14': 22,
            'GV4': 49,
            'GV5': 49,
            'GV6': 82,
            'GV7': 49,
            'GV8': 49,
            'GV16': 71,
            'GV20': 107,
            'GV18': 22,
            }

    def set_driver_uom(self, units):
        if units == 'metric':
            self.uom['BARPRES'] = 117
            self.uom['GV0'] = 4
            self.uom['GV1'] = 4
            self.uom['GV19'] = 25
            self.uom['GV4'] = 49
            self.uom['GV5'] = 49
            self.uom['GV6'] = 82
            self.uom['GV7'] = 49
            self.uom['GV8'] = 49
            self.uom['GV20'] = 107
        elif units == 'imperial':
            self.uom['BARPRES'] = 23
            self.uom['GV0'] = 17
            self.uom['GV1'] = 17
            self.uom['GV19'] = 25
            self.uom['GV4'] = 48
            self.uom['GV5'] = 48
            self.uom['GV6'] = 105
            self.uom['GV7'] = 48
            self.uom['GV8'] = 48
            self.uom['GV20'] = 106


    def mm2inch(self, mm):
        return mm/25.4


    '''
        self.fcast['temp_max']
        self.fcast['temp_min']
        self.fcast['Hmax']
        self.fcast['Hmin']
        self.fcast['pressure']
        self.fcast['speed']
        self.fcast['speed_max']
        self.fcast['speed_min']
        self.fcast['gust']
        self.fcast['gust_max']
        self.fcast['gust_min']
        self.fcast['dir']
        self.fcast['dir_max']
        self.fcast['dir_min']
        self.fcast['timestamp']
        self.fcast['pop']
        self.fcast['precip']
        self.fcast['uv']
        self.fcast['clouds']
    '''
    def update_forecast(self, forecast, latitude, elevation, plant_type, units):

        epoch = int(forecast['timestamp'])
        dow = time.strftime("%w", time.gmtime(epoch))
        LOGGER.info('Day of week = ' + dow)

        humidity = (forecast['Hmin'] + forecast['Hmax']) / 2
        self.setDriver('CLIHUM', round(humidity, 0), True, False, self.uom['CLIHUM'])
        self.setDriver('BARPRES', round(forecast['pressure'], 1), True, False, self.uom['BARPRES'])
        self.setDriver('GV0', round(forecast['temp_max'], 1), True, False, self.uom['GV0'])
        self.setDriver('GV1', round(forecast['temp_min'], 1), True, False, self.uom['GV1'])
        self.setDriver('GV14', round(forecast['clouds'], 0), True, False, self.uom['GV14'])
        self.setDriver('GV4', round(forecast['speed'], 1), True, False, self.uom['GV4'])
        self.setDriver('GV5', round(forecast['gust'], 1), True, False, self.uom['GV5'])
        self.setDriver('GV6', round(forecast['precip'], 1), True, False, self.uom['GV6'])
        self.setDriver('GV7', round(forecast['speed_max'], 1), True, False, self.uom['GV7'])
        self.setDriver('GV8', round(forecast['speed_min'], 1), True, False, self.uom['GV8'])

        self.setDriver('GV19', int(dow), True, False, self.uom['GV19'])
        self.setDriver('GV16', round(forecast['uv'], 1), True, False, self.uom['GV16'])
        self.setDriver('GV18', round(forecast['pop'], 1), True, False, self.uom['GV18'])
        self.setDriver('GV11', forecast['coverage'], True, False, self.uom['GV11'])
        self.setDriver('GV12', forecast['intensity'], True, False, self.uom['GV12'])
        self.setDriver('GV13', forecast['weather'], True, False, self.uom['GV13'])

        # Calculate ETo
        #  Temp is in degree C and windspeed is in m/s, we may need to
        #  convert these.
        J = datetime.datetime.fromtimestamp(epoch).timetuple().tm_yday

        Tmin = forecast['temp_min']
        Tmax = forecast['temp_max']
        Ws = forecast['speed']
        if units != 'si':
            LOGGER.info('Conversion of temperature/wind speed required')
            Tmin = et3.FtoC(Tmin)
            Tmax = et3.FtoC(Tmax)
            Ws = et3.mph2ms(Ws)
        else:
            Ws = et3.kph2ms(Ws)

        et0 = et3.evapotranspriation(Tmax, Tmin, None, Ws, float(elevation), forecast['Hmax'], forecast['Hmin'], latitude, float(plant_type), J)
        self.setDriver('GV20', round(et0, 2), True, False)
        LOGGER.info("ETo = %f %f" % (et0, self.mm2inch(et0)))
