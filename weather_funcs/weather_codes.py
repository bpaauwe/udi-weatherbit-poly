class codes:
    @staticmethod
    def weather_codes(self, code):
        code_map = {
                'A': 0,   # hail
                'BD': 1,  # blowing dust
                'BN': 2,  # blowing sand
                'BR': 3,  # mist
                'BS': 4,  # blowing snow
                'BY': 5,  # blowing spray
                'F': 6,   # fog
                'FR': 7,  # frost
                'H': 8,   # haze
                'IC': 9,  # ice crystals
                'IF': 10, # ice fog
                'IP': 11, # ice pellets / Sleet
                'K': 12,  # smoke
                'L': 13,  # drizzle
                'R': 14,  # rain
                'RW': 15, # rain showers
                'RS': 16, # rain/snow mix
                'SI': 17, # snow/sleet mix
                'WM': 18, # wintry mix (sno, sleet, rain)
                'S': 19,  # snow
                'SW': 20, # snow showers
                'T': 21,  # Thunderstorms
                'UP': 22, # unknown precipitation
                'VA': 23, # volcanic ash
                'WP': 24, # waterspouts
                'ZF': 25, # freezing fog
                'ZL': 26, # freezing drizzle
                'ZR': 27, # freezing rain
                'ZY': 28, # freezing spray
                'CL': 29, # Clear
                'FW': 30, # Fair/Mostly sunny
                'SC': 31, # Partly cloudy
                'BK': 32, # Mostly cloudy
                'OV': 33, # Cloudy/Overcast
                }

        if code in code_map:
            return code_map[code]

        return 22

    @staticmethod
    def intensity_codes(self, code):
        code_map = {
                'VL': 1,  # very light
                'L': 2,   # light
                'H': 3,   # heavy
                'VH': 4,  # very heavy
                }
        if code in code_map:
            return code_map[code]
        return 0  # moderate

    @staticmethod
    def coverage_codes(self, code):
        code_map = {
                'AR': 0,  # areas of
                'BR': 1,  # brief
                'C':  2,  # chance of
                'D':  3,  # definite
                'FQ': 4,  # frequent
                'IN': 5,  # intermittent
                'IS': 6,  # isolated
                'L':  7,  # likely
                'NM': 8,  # numerous
                'O':  9,  # occasional
                'PA': 10,  # patchy
                'PD': 11,  # periods of
                'S':  12,  # slight chance
                'SC': 13,  # scattered
                'VC': 14,  # in the vicinity/nearby
                'WD': 15,  # widespread
                }
        if code in code_map:
            return code_map[code]
        return 16

