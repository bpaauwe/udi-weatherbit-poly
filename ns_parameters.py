"""
    Functions to handle custom parameters.

    pass in a list of name and default value parameters
    [
        {'name': name of parameter,
         'default': default value of parameter,
        },
        {'name': name of parameter,
         'default': default value of parameter,
        },
    ]

"""

class NSParameters:
    def __init__(self, parameters):
        self.internal = []

        for p in parameters:
            self.internal.append({
                'name': p['name'],
                'value': '', 
                'default': p['default'],
                'isSet': False,
                'isRequired': p['isRequired'],
                })

    def set(self, name, value):
        for p in self.internal:
            if p['name'] == name:
                p['value'] = value
                p['isSet'] = True
                return

    def get(self, name):
        for p in self.internal:
            if p['name'] == name:
                if p['isSet']:
                    return p['value']
                else:
                    return p['default']

    """
        Read paramenters from Polyglot and update values appropriately.

        return True if all required parameters are set to non-default values
        otherwise return False
    """
    def get_from_polyglot(self, poly):
        customParams = poly.polyConfig['customParams']
        params = {}

        for p in self.internal:
            if p['name'] in customParams:
                p['value'] = customParams[p['name']]
                if p['value'] != p['default']:
                    p['isSet'] = True
            
            if p['isSet']:
                params[p['name']] = p['value']
            else:
                params[p['name']] = p['default']

        poly.addCustomParam(params)            

        for p in self.internal:
            if not p['isSet'] and p['isRequired']:
                return False
        return True


    """
        Called from process_config to check for configuration change
    """
    def update_from_polyglot(self, config):
        if 'customParams' in config:
            for p in self.internal:
                if p['name'] in config['customParams']:
                    if config['customparams'][p['name']] != p['default']:
                        p['value'] = config['customParams'][p['name']]
                        p['isSet'] = True

        for p in self.internal:
            if not p['isSet'] and p['isRequired']:
                return False
        return True


