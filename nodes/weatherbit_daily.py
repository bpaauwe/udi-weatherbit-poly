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
from weather_funcs import weather_codes
from weather_funcs import et3

LOGGER = polyinterface.LOGGER

class DailyNode(polyinterface.Node):
    id = 'daily'
    # TODO: add wind speed min/max, pop, winddir min/max
    drivers = [
            {'driver': 'GV19', 'value': 0, 'uom': 25},     # day of week
            {'driver': 'GV0', 'value': 0, 'uom': 4},       # high temp
            {'driver': 'GV1', 'value': 0, 'uom': 4},       # low temp
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'DEWPT', 'value': 0, 'uom': 4},     # dewpoint
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # clouds
            {'driver': 'GV4', 'value': 0, 'uom': 49},      # wind speed
            {'driver': 'GV5', 'value': 0, 'uom': 49},      # gust speed
            {'driver': 'WINDDIR', 'value': 0, 'uom': 76},  # wind dir
            {'driver': 'GV6', 'value': 0, 'uom': 82},      # precipitation
            {'driver': 'GV7', 'value': 0, 'uom': 82},      # snow
            {'driver': 'GV8', 'value': 0, 'uom': 82},      # snow depth
            {'driver': 'GV18', 'value': 0, 'uom': 22},     # pop
            {'driver': 'GV16', 'value': 0, 'uom': 71},     # UV index
            {'driver': 'GV10', 'value': 0, 'uom': 56},     # ozone
            {'driver': 'GV15', 'value': 0, 'uom': 83},     # visibility
            {'driver': 'GV9', 'value': 0, 'uom': 56},      # moon phase
            {'driver': 'GV20', 'value': 0, 'uom': 106},    # mm/day
            ]
    uom = {'GV19': 25,
            'GV0': 4,
            'GV1': 4,
            'CLIHUM': 22,
            'DEWPT': 4,
            'BARPRES': 117,
            'GV11': 25,
            'GV12': 25,
            'GV13': 25,
            'GV14': 22,
            'GV4': 49,
            'GV5': 49,
            'GV6': 82,
            'GV7': 82,
            'GV8': 82,
            'GV16': 71,
            'GV20': 107,
            'GV15': 83,
            'GV18': 22,
            'GV10': 56,
            'GV9': 56,
            'WINDDIR': 76,
            }

    def set_driver_uom(self, units):
        if units == 'metric':
            self.units = 'metric'
            self.uom['BARPRES'] = 117
            self.uom['GV0'] = 4
            self.uom['GV1'] = 4
            self.uom['GV19'] = 25
            self.uom['GV4'] = 49
            self.uom['GV5'] = 49
            self.uom['GV6'] = 82
            self.uom['GV7'] = 82
            self.uom['GV8'] = 82
            self.uom['GV20'] = 107
            self.uom['GV15'] = 83
            self.uom['DEWPT'] = 4
            self.uom['WINDIR'] = 76
        elif units == 'imperial':
            self.units = 'imperial'
            self.uom['BARPRES'] = 117
            self.uom['GV0'] = 17
            self.uom['GV1'] = 17
            self.uom['GV19'] = 25
            self.uom['GV4'] = 48
            self.uom['GV5'] = 48
            self.uom['GV6'] = 105
            self.uom['GV7'] = 105
            self.uom['GV8'] = 105
            self.uom['GV20'] = 106
            self.uom['GV15'] = 116
            self.uom['DEWPT'] = 17
            self.uom['WINDIR'] = 76


    def mm2inch(self, mm):
        return mm/25.4


    def update_driver(self, driver, value):
        try:
            self.setDriver(driver, value, True, False, self.uom[driver])
        except:
            LOGGER.debug('Failed to set driver ' + driver + ' to value ' + value)

    '''
    '''
    def update_forecast(self, forecast, elevation, plant_type, latitude):

        epoch = int(forecast['ts'])
        dow = time.strftime("%w", time.gmtime(epoch))
        LOGGER.info('Day of week = ' + dow)

        self.update_driver('CLIHUM', forecast['rh'])
        self.update_driver('BARPRES', forecast['pres'])
        self.update_driver('DEWPT', forecast['dewpt'])
        self.update_driver('GV0', forecast['max_temp'])
        self.update_driver('GV1', forecast['min_temp'])
        self.update_driver('GV14', forecast['clouds'])
        self.update_driver('GV4', forecast['wind_spd'])
        self.update_driver('GV5', forecast['wind_gust_spd'])
        self.update_driver('WINDDIR', forecast['wind_dir'])
        self.update_driver('GV6', forecast['precip'])
        self.update_driver('GV7', forecast['snow'])
        self.update_driver('GV8', forecast['snow_depth'])
        self.update_driver('GV19', int(dow))
        self.update_driver('GV16', forecast['uv'])
        self.update_driver('GV15', forecast['vis'])
        self.update_driver('GV18', forecast['pop'])
        self.update_driver('GV10', forecast['ozone'])
        self.update_driver('GV9', forecast['moon_phase'])
        # moon_phase, 
        # pod = part of day d=day, n=night
        # forecast['weather']['code']
        self.update_driver('GV13', forecast['weather']['code'])

        # Calculate ETo
        #  Temp is in degree C and windspeed is in m/s, we may need to
        #  convert these.
        J = datetime.datetime.fromtimestamp(epoch).timetuple().tm_yday

        Tmin = forecast['min_temp']
        Tmax = forecast['max_temp']
        Ws = forecast['wind_spd']
        if self.units != 'metric':
            LOGGER.info('Conversion of temperature/wind speed required')
            Tmin = et3.FtoC(Tmin)
            Tmax = et3.FtoC(Tmax)
            Ws = et3.mph2ms(Ws)

        et0 = et3.evapotranspriation(Tmax, Tmin, None, Ws, float(elevation), forecast['rh'], forecast['rh'], latitude, float(plant_type), J)
        self.update_driver('GV20', round(et0, 2))
        LOGGER.info("ETo = %f %f" % (et0, self.mm2inch(et0)))
