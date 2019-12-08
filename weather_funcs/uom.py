#
#  Unit of Measure configuration function
#
#  Return a dictionary with driver names as the key and the UOM for
#  the requested unit configuration.
#
#  valid unit configurations are:
#   metric, imperial, si (same as metric), us (same as imperial), uk
#
#  Ideally, there should be no conflicts between forecast and current
#  condition driver types


def get_uom(units):
    unit_cfg = units.lower()

    if unit_cfg == 'metric' or unit_cfg == 'si' or unit_cfg.startswith('m'):
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 4,   # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 117, # pressure
            'WINDDIR': 76,  # direction
            'DEWPT': 4,     # dew point
            'SOLRAD': 74,   # solar radiation
            'GV0': 4,       # max temp
            'GV1': 4,       # min temp
            'GV2': 4,       # feels like
            'GV4': 49,      # wind speed
            'GV5': 49,      # wind gusts
            'GV6': 82,      # rain
            'GV7': 82,      # snow
            'GV8': 82,      # snow depth
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 83,     # visibility
            'GV16': 71,     # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 107,    # ETo
        }
    elif unit_cfg == 'uk':
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 4,   # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 117, # pressure
            'WINDDIR': 76,  # direction
            'DEWPT': 4,     # dew point
            'SOLRAD': 74,   # solar radiation
            'GV0': 4,       # max temp
            'GV1': 4,       # min temp
            'GV2': 4,       # feels like
            'GV4': 48,      # wind speed
            'GV5': 48,      # wind gusts
            'GV6': 105,     # rain
            'GV7': 82,      # snow
            'GV8': 82,      # snow depth
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 116,    # visibility
            'GV16': 71,     # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 107,    # ETo
        }
    else:
        uom = {
            'ST': 2,   # node server status
            'CLITEMP': 17,  # temperature
            'CLIHUM': 22,   # humidity
            'BARPRES': 117, # pressure (always mb)
            'WINDDIR': 76,  # direction
            'DEWPT': 17,    # dew point
            'SOLRAD': 74,   # solar radiation
            'GV0': 17,      # max temp
            'GV1': 17,      # min temp
            'GV2': 17,      # feels like
            'GV4': 48,      # wind speed
            'GV5': 48,      # wind gusts
            'GV6': 105,     # rain
            'GV7': 105,     # snow
            'GV8': 105,     # snow depth
            'GV9': 56,      # moon phase
            'GV10': 56,     # ozone
            'GV11': 25,     # climate coverage
            'GV12': 25,     # climate intensity
            'GV13': 25,     # climate conditions
            'GV14': 22,     # cloud conditions
            'GV15': 116,    # visibility
            'GV16': 71,     # UV index
            'GV17': 56,     # Air Quality
            'GV18': 22,     # chance of precipitation
            'GV19': 25,     # day of week
            'GV20': 106,    # ETo
        }

    return uom
