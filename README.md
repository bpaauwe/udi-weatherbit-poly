
# WeatherBit weather service

This is a node server to pull weather data from the WeatherBit weather network and make it available to a [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)

(c) 2019 Robert Paauwe
MIT license.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server per configuration section below.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the WeatherBit weather service for current condition data. Note that the free plan only updates data hourly. Setting this to less may result in exceeding the free service rate limit.
#### Long Poll
   * How often to poll the WeatherBit weather service for forecast data. Note that the free plan only updates data hourly. Setting this to less may result in exceeding the free service rate limit.

#### APIkey
	* Your API ID, needed to authorize connection to the WeatherBit API.
#### Elevation 
	* The elevation, in meters, of the location. Default is 0
#### Forecast Days
	* The number of days of forecast data to track (0 - 16)
#### Location 
	* Location to get data for.  Can be specified as:
    - lat&lon      Ex: lat=38.123&lon=-78.543
	- city,state   Ex: city=Raleigh,NC
	- city&contry  Ex: city=Raleigh&country=US
	- city_id      Ex: city_id=8953360
	- station      Ex: station=KSEA
	- postal_code  Ex: postal_code=27601
	- postal_code&country   Ex: postal_code=27601&country=US
#### Plant Type
	* Used as part of the ETo calculation to compensate for different types of ground cover.  Default is 0.23
#### Units    
	* M for si and I for imperial. Default is M

To get an API key, register at www.weatherbit.io



## Requirements

1. Polyglot V2 itself should be run on Raspian Stretch.
  To check your version, ```cat /etc/os-release``` and the first line should look like
  ```PRETTY_NAME="Raspbian GNU/Linux 9 (stretch)"```. It is possible to upgrade from Jessie to
  Stretch, but I would recommend just re-imaging the SD card.  Some helpful links:
   * https://www.raspberrypi.org/blog/raspbian-stretch/
   * https://linuxconfig.org/raspbian-gnu-linux-upgrade-from-jessie-to-raspbian-stretch-9
2. This has only been tested with ISY 5.0.14 so it is not guaranteed to work with any other version.

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "WeatherBit Weather".

For Polyglot 2.0.35, hit "Cancel" in the update window so the profile will not be updated and ISY rebooted.  The install procedure will properly handle this for you.  This will change with 2.0.36, for that version you will always say "No" and let the install procedure handle it for you as well.

Then restart the nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 1.0.8 07/07/2020
   - Convert int to string for display in debug message.
- 1.0.7 06/11/2020
   - Correrct UOM for ETo.
- 1.0.6 04/11/2020
   - Snow depth was incorrectly renamed to rain today, rename it back.
- 1.0.5 04/10/2020
   - Current conditions report rain rate not rain accumulation
- 1.0.4 03/16/2020
   - Change first forecast address to forecast_0 to match other weather node servers.
- 1.0.3 12/31/2019
   - Fix bug when forecast days is set to zero.
- 1.0.2 12/19/2019
   - Fix bug that prevented custom parameter changes from taking immediate
     effect.
- 1.0.1 12/18/2019
   - Use correct UOM (74) for solar radiation
- 1.0.0 12/08/2019
   - Initial version published to github 
