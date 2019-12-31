## Configuration

The WeatherBit.io node server has the following user configuration
parameters:

- APIkey   : Your API ID, needed to authorize connection to the WeatherBit API.
- Elevation : The elevation, in meters, of the location. Default is 0
- Forecast Days: The number of days of forecast data to track (0 - 16)
- Location : Location to get data for.  Can be specified as:
    - lat&lon      Ex: lat=38.123&lon=-78.543
	- city,state   Ex: city=Raleigh,NC
	- city&contry  Ex: city=Raleigh&country=US
	- city\_id      Ex: city\_id=8953360
	- station      Ex: station=KSEA
	- postal\_code  Ex: postal\_code=27601
	- postal\_code&country   Ex: postal\_code=27601&country=US
- Plant Type: Used as part of the ETo calculation to compensate for different types of ground cover.  Default is 0.23
- Units    : M for si and I for imperial. Default is M

To get an API key, register at www.weatherbit.io

