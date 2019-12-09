#
#  Common functions used by nodes


try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface


LOGGER = polyinterface.LOGGER

def add_functions_as_methods(functions):
    def decorator(Class):
        for function in functions:
            setattr(Class, function.__name__, function)
        return Class
    return decorator

# Wrap all the setDriver calls so that we can check that the 
# value exist first.
def update_driver(self, driver, value, force=False, prec=3):
    try:
        self.setDriver(driver, round(float(value), prec), True, force, self.uom[driver])
        LOGGER.debug('setDriver (%s, %f)' %(driver, float(value)))
    except:
        LOGGER.warning('Missing data for driver ' + driver)

def get_saved_log_level(self):
    if 'customData' in self.polyConfig:
        if 'level' in self.polyConfig['customData']:
            return self.polyConfig['customData']['level']

    return 0

def save_log_level(self, level):
    level_data = {
            'level': level,
            }
    self.poly.saveCustomData(level_data)

functions = (update_driver, get_saved_log_level, save_log_level)
