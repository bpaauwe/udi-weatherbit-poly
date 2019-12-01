#!/usr/bin/env python3
"""
Polyglot v2 node server WeatherBit weather data
Copyright (C) 2019 Robert Paauwe
"""
import sys
import time
try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
from nodes import Controller
from nodes import weatherbit_daily

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('WeatherBit')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

