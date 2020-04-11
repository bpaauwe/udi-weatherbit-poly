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
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'weather'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'WeatherBit Weather'
        self.address = 'weather'
        self.primary = self.address
        self.configured = False
        self.uom = {}

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
            LOGGER.debug('-- configuration not changed, but is valid')
            # is this necessary
            #self.configured = True

    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
        self.discover()

        LOGGER.info('Node server started')

        # Do an initial query to get filled in as soon as possible
        self.query_conditions(True)
        self.query_forecast(True)

    def longPoll(self):
        self.query_forecast(False)

    def shortPoll(self):
        self.query_conditions(False)

    def get_weather_data(self, url_param, extra=None):
        request = 'http://api.weatherbit.io/v2.0/'
        request += url_param
        request += '?' + self.params.get('Location')
        request += '&key=' + self.params.get('APIkey')
        request += '&units=' + self.params.get('Units')

        if extra != None:
            request += extra

        LOGGER.debug('request = %s' % request)

        try:
            c = requests.get(request)
            jdata = c.json()
            c.close()

            LOGGER.debug(jdata)
        except:
            LOGGER.error('HTTP request failed for ' + url_param)
            jdata = {}

        return jdata

    """
        Query the weather service for the current conditions and update
        the current condition node values.
    """
    def query_conditions(self, force):


        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        jdata = self.get_weather_data('current')

        # Should we check that jdata actually has something in it?
        if jdata == None:
            LOGGER.error('Current condition query returned no data')
            return

        if 'data' not in jdata:
            LOGGER.error('No response object in query response.')
            return

        ob = jdata['data'][0] # Only use first observation record

        self.update_driver('CLITEMP', ob['temp'], force)
        self.update_driver('CLIHUM', ob['rh'], force)
        self.update_driver('BARPRES', ob['pres'], force)
        self.update_driver('GV4', ob['wind_spd'], force)
        self.update_driver('WINDDIR', ob['wind_dir'], force)
        self.update_driver('GV15', ob['vis'], force)
        self.update_driver('GV6', ob['precip'], force)
        self.update_driver('DEWPT', ob['dewpt'], force)
        self.update_driver('GV2', ob['app_temp'], force)
        self.update_driver('SOLRAD', ob['solar_rad'], force)
        self.update_driver('GV16', ob['uv'], force, 1)
        self.update_driver('GV17', ob['aqi'], force)
        self.update_driver('GV14', ob['clouds'], force)

        # Weather conditions:
        #  ob['weather'][code]
        weather = ob['weather']['code']
        LOGGER.debug('**>>> WeatherCoded = ' + weather)
        self.update_driver('GV13', weather, force)

    # TODO: Move query_forecast to the daily node file
    def query_forecast(self, force):
        # daily forecasts

        days = '&days=' + self.params.get('Forecast Days')

        if days == 0:  # skip if no forecast days defined.
            return

        jdata = self.get_weather_data('forecast/daily', days)

        if not self.configured:
            LOGGER.info('Skipping connection because we aren\'t configured yet.')
            return

        if 'data' not in jdata:
            LOGGER.error('No response object in query response.')
            return

        day = 0
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
            for day in range(num_days, 16):
                address = 'forecast_' + str(day)
                try:
                    self.delNode(address)
                except:
                    LOGGER.debug('Failed to delete node ' + address)

        for day in range(0, num_days):
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
        self.uom =  uom.get_uom(units)
        for day in range(0,int(self.params.get('Forecast Days'))):
            address = 'forecast_' + str(day)
            self.nodes[address].set_driver_uom(units)

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def set_logging_level(self, level=None):
        if level is None:
            try:
                #level = self.getDriver('GV21')
                level = self.get_saved_log_level()
            except:
                LOGGER.error('set_logging_level: get GV21 value failed.')

            if level is None:
                level = 30
            level = int(level)
        else:
            level = int(level['value'])

        #self.setDriver('GV21', level, True, True)
        self.save_log_level(level)

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
            {'driver': 'RAINRT', 'value': 0, 'uom': 46},   # rain
            {'driver': 'GV13', 'value': 0, 'uom': 25},     # climate conditions
            {'driver': 'GV14', 'value': 0, 'uom': 22},     # cloud conditions
            {'driver': 'GV15', 'value': 0, 'uom': 83},     # visibility
            {'driver': 'GV16', 'value': 0, 'uom': 71},     # uv
            {'driver': 'GV17', 'value': 0, 'uom': 56},     # air quality
            {'driver': 'SOLRAD', 'value': 0, 'uom': 74},   # solar radiataion
            {'driver': 'GV21', 'value': 0, 'uom': 25},     # log level
            ]

