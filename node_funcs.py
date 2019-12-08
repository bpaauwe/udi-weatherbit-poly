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

functions = (update_driver, )
