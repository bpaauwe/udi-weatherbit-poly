#!/usr/bin/env python3
"""
Polyglot v2 node server WeatherBit weather data
Copyright (C) 2019 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import datetime
import requests
import socket
import math
import re
import json
from nodes import weatherbit_daily
from weather_funcs import *
import ns_parameters

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    id = 'weather'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'WeatherBit Weather'
        self.address = 'weather'
        self.primary = self.address
        self.units = 'M'
        self.configured = False
        self.latitude = 0
        self.longitude = 0
        self.fcast = {}
        self.uom = {}
        self.tag = {}

        self.params = ns_parameters.NSParameters([{
            'name': 'APIkey',
            'default': 'set me',
            'isRequired': True,
            'notice': 'WeatherBit API ID must be set',
            },
            {
            'name': 'Location',
            'default': 'set me',
            'isRequired': True,
            'notice': 'WeatherBit Location must be set',
            },
            {
            'name': 'Elevation',
            'default': '0',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Units',
            'default': 'M',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Forecast Days',
            'default': '0',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Plant Type',
            'default': '0.23',
            'isRequired': False,
            'notice': '',
            },
            ])

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            LOGGER.debug('-- configuration not yet valid')
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            LOGGER.debug('-- configuration is valid')
            self.removeNoticesAll()
            self.configured = True
            if self.params.isSet('Forecast Days'):
                self.discover()
        elif valid:
            LOGGER.debug('-- configuration not changaed, but is valid')
            # is this necessary
            #self.configured = True

    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
        self.discover()

        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_conditions()
        self.query_forecast()

    def longPoll(self):
        self.query_forecast()

    def shortPoll(self):
        self.query_conditions()

    # Wrap all the setDriver calls so that we can check that the 
    # value exist first.
    def update_driver(self, driver, value):
        try:
            self.setDriver(driver, float(value), report=True, force=False, uom=self.uom[driver])
            #LOGGER.info('setDriver (%s, %f)' %(driver, float(value)))
        except:
            LOGGER.debug('Missing data for driver ' + driver)


    """
        Query the weather service for the current conditions and update
        the current condition node values.
    """
    def query_conditions(self):

        # build query URL
        request = 'http://api.weatherbit.io/v2.0/current'
        if re.fullmatch(r'\d\d\d\d\d,..', self.params.get('Location')) != None:
            request += '?' + self.params.get('Location')
        elif re.fullmatch(r'\d\d\d\d\d', self.params.get('Location')) != None:
            request += '?' + self.params.get('Location')
        else:
            request += '?' + self.params.get('Location')

        request += '&key=' + self.params.get('APIkey')
        request += '&units=' + self.params.get('Units')

        LOGGER.debug('request = %s' % request)

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        c = requests.get(request)
        jdata = c.json()
        c.close()
        LOGGER.debug(jdata)

        # Should we check that jdata actually has something in it?
        if jdata == None:
            LOGGER.error('Current condition query returned no data')
            return

        if 'data' not in jdata:
            LOGGER.error('No response object in query response.')
            return

        ob = jdata['data'][0] # Only use first observation record

        self.update_driver('CLITEMP', ob['temp'])
        self.update_driver('CLIHUM', ob['rh'])
        self.update_driver('BARPRES', ob['pres'])
        self.update_driver('GV4', ob['wind_spd'])
        self.update_driver('WINDDIR', ob['wind_dir'])
        self.update_driver('GV15', ob['vis'])
        self.update_driver('GV6', ob['precip'])
        self.update_driver('DEWPT', ob['dewpt'])
        self.update_driver('GV2', ob['app_temp'])
        self.update_driver('SOLRAD', ob['solar_rad'])
        self.update_driver('GV16', ob['uv'])
        self.update_driver('GV17', ob['aqi'])

        # Weather conditions:
        #  ob['weather'][code]
        weather = ob['weather']['code']
        LOGGER.debug('**>>> WeatherCoded = ' + weather)
        self.update_driver('GV13', weather)

        # cloud cover
        self.update_driver('GV14', ob['clouds'])

    # TODO: Move query_forecast to the daily node file
    def query_forecast(self):
        # daily forecasts

        request = 'http://api.weatherbit.io/v2.0/forecast/daily'
        request += '?' + self.params.get('Location')
        request += '&key=' + self.params.get('APIkey')
        request += '&units=' + self.params.get('Units')
        request += '&days=' + self.params.get('Forecast Days')

        LOGGER.debug('request = %s' % request)

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        c = requests.get(request)
        jdata = c.json()
        c.close()

        day = 1
        # first day is today, is that OK
        for f_obs in jdata['data']:
            LOGGER.debug('forecast for date ' + f_obs['valid_date'])
            address = 'forecast_' + str(day)
            self.nodes[address].update_forecast(f_obs, float(self.params.get('Elevation')), float(self.params.get('Plant Type')), float(jdata['lat']))
            day += 1


    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        num_days = int(self.params.get('Forecast Days'))
        LOGGER.info('Creating nodes for %d days of forecast data' % num_days);

        if num_days < 16:
            # if less than 16 days should we try to delete extras?
            for day in range(num_days + 1, 16):
                address = 'forecast_' + str(day)
                try:
                    self.delNode(address)
                except:
                    LOGGER.debug('Failed to delete node ' + address)

        if num_days == 0:
            return

        for day in range(1, num_days + 1):
            address = 'forecast_' + str(day)
            title = 'Forecast ' + str(day)
            try:
                node = weatherbit_daily.DailyNode(self, self.address, address, title)
                self.addNode(node)
            except:
                LOGGER.error('Failed to create forecast node ' + title)

        self.set_driver_uom(self.params.get('Units'))


    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):

        # NEW code, try this:
        self.removeNoticesAll()

        if self.params.get_from_polyglot(self):
            LOGGER.debug('All required parameters are set!')
            self.configured = True
            if int(self.params.get('Forecast Days')) > 16:
                addNotice('Number of days of forecast data limited to 16 days', 'forecast')
                self.params.set('Forcast Days', 16)
        else:
            LOGGER.debug('Configuration required.')
            LOGGER.debug('apikey = ' + self.params.get('APIkey'))
            LOGGER.debug('location = ' + self.params.get('Location'))
            self.params.send_notices(self)

    # Set the uom dictionary based on current user units preference
    def set_driver_uom(self, units):
        LOGGER.info('New Configure driver units to ' + units)
        if units == 'M':
            self.uom['ST'] = 2   # node server status
            self.uom['CLITEMP'] = 4   # temperature
            self.uom['CLIHUM'] = 22   # humidity
            self.uom['BARPRES'] = 117 # pressure
            self.uom['WINDDIR'] = 76  # direction
            self.uom['DEWPT'] = 4     # dew point
            self.uom['GV0'] = 4       # max temp
            self.uom['GV1'] = 4       # min temp
            self.uom['GV2'] = 4       # feels like
            self.uom['GV4'] = 49      # wind speed
            self.uom['GV5'] = 49      # wind gusts
            self.uom['GV6'] = 82      # rain
            self.uom['GV11'] = 25     # climate coverage
            self.uom['GV12'] = 25     # climate intensity
            self.uom['GV13'] = 25     # climate conditions
            self.uom['GV14'] = 22     # cloud conditions
            self.uom['GV15'] = 83     # visibility
            self.uom['GV16'] = 71     # UV index
            self.uom['GV17'] = 56     # Air Quality
            self.uom['SOLRAD'] = 74   # solar radiation

            for day in range(1,int(self.params.get('Forecast Days')) + 1):
                address = 'forecast_' + str(day)
                self.nodes[address].set_driver_uom('metric')
        else:
            self.uom['ST'] = 2   # node server status
            self.uom['CLITEMP'] = 17  # temperature
            self.uom['CLIHUM'] = 22   # humidity
            self.uom['BARPRES'] = 23  # pressure
            self.uom['WINDDIR'] = 76  # direction
            self.uom['DEWPT'] = 17    # dew point
            self.uom['GV0'] = 17      # max temp
            self.uom['GV1'] = 17      # min temp
            self.uom['GV2'] = 17      # feels like
            self.uom['GV4'] = 48      # wind speed
            self.uom['GV5'] = 48      # wind gusts
            self.uom['GV6'] = 105     # rain
            self.uom['GV11'] = 25     # climate coverage
            self.uom['GV12'] = 25     # climate intensity
            self.uom['GV13'] = 25     # climate conditions
            self.uom['GV14'] = 22     # cloud conditions
            self.uom['GV15'] = 116    # visibility
            self.uom['GV16'] = 71     # UV index
            self.uom['GV17'] = 56     # Air Quality
            self.uom['SOLRAD'] = 74   # solar radiation

            for day in range(1,int(self.params.get('Forecast Days')) + 1):
                address = 'forecast_' + str(day)
                self.nodes[address].set_driver_uom('imperial')

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                level = self.getDriver('GV21')
            except:
                LOGGER.error('set_logging_level: get GV21 value failed.')

            if level is None:
                level = 30
            level = int(level)
        else:
            level = int(level['value'])

        self.setDriver('GV21', level)

        LOGGER.info('set_logging_level: Setting log level to %d' % level)
        LOGGER.setLevel(level)


    commands = {
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'DEBUG': set_logging_level,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            {'driver': 'CLITEMP', 'value': 0, 'uom': 4},   # temperature
            {'driver': 'CLIHUM', 'value': 0, 'uom': 22},   # humidity
            {'driver': 'DEWPT', 'value': 0, 'uom': 4},     # dewpoint
            {'driver': 'BARPRES', 'value': 0, 'uom': 117}, # pressure
            {'driver': 'WINDDIR', 'value': 0, 'uom': 76},  # direction
            {'driver': 'GV4', 'value': 0, 'uom': 49},      # wind speed
            {'driver': 'GV2', 'value': 0, 'uom': 4},       # feels like
            {'driver': 'GV6', 'value': 0, 'uom': 82},      # rain
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # climate conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # cloud conditions
            {'driver': 'GV15', 'value': 0, 'uom': 83},     # visibility
            {'driver': 'GV17', 'value': 0, 'uom': 56},     # air quality
            {'driver': 'SOLRAD', 'value': 0, 'uom': 71},   # solar radiataion
            ]

