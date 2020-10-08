import urllib2
import json
import pytz
from datetime import datetime

class Daylight(object):
    """Daylight gets and caches sunrise and sunset data from a configurable webservice."""

    config = None
    logger = None

    url = None
    location = None
    timezone = None

    # The Webservice has a fair use policy so we store the data localy to minimise
    # the amount of fetches. The data is only fetched if the localstore has no or stale data.
    # We store Strings in the dictionary so we can use standard json operations
    # to and from the local datastore.
    datastore = None
    data = {
        "sunrise": "",
        "sunset": ""
    }

    def __init__(self, config, logger):
        super(Daylight, self).__init__()
        self.config = config
        self.logger = logger

        self.url = self.config.get('daylight', 'url')
        self.location = self.config.get('daylight', 'location')
        self.timezone = self.config.get('daylight', 'timezone')
        self.datastore = self.config.get('daylight', 'datastore')

        self.__load_Data()

    def __save_Data(self):
        self.logger.debug('Saving daylight data to: ' + self.datastore)

        try:
            fp = open(self.datastore, "w")

            json.dump(self.data, fp)
        except IOError:
            self.logger.error('I/O Error saving data to ' + self.datastore + '. Aborting...')
            fp.close
            return False

        return True

    def __load_Data(self):
        self.logger.debug('Trying to load daylight data from: ' + self.datastore)

        try:
            fp = open(self.datastore, "r+")

            self.data = json.load(fp)
        except IOError:
            self.logger.debug('I/O Error reading ' + self.datastore + '. Creating file...')
        except ValueError:
            fp.close
            return False

        return True

    def __get_NewData(self):

        rawdata = None

        # https://api.sunrise-sunset.org/json?lat=53.123621&lng=6.286966
        # returns all datetime objects in UTC (GMT)
        #url = "https://api.sunrise-sunset.org/json"
        #location = "lat=53.123621&lng=6.286966"

        request_object = urllib2.Request(self.url + '?' + self.location)

        self.logger.info('Fetching new daylight data from: ' + self.url + '?' + self.location)

        try:
            response = urllib2.urlopen(request_object)
            rawdata = json.load(response)
            self.logger.debug('Fetched data: '+ json.dumps(rawdata))

        except urllib2.HTTPError, e:
            self.logger.error('HTTPError = ' + str(e.code) + ' Aborting...')
            return False
        except urllib2.URLError, e:
            self.logger.error('URLError = ' + str(e.reason) + ' Aborting...')
            return False
        except ValueError, e:
            self.logger.error('ValueError = ' + str(e.reason) + ' Aborting...')
            return False

        if(rawdata['status'] != 'OK'):
            self.logger.error('Status code is: ' + rawdata['status'] + ' This is not OK. Aborting...')
            return False

        # All date/times from this Webservice are delivered in UTC. We convert to Local times.
        now_utc = datetime.now(pytz.utc)

        sunrise_utc = datetime.combine(now_utc.date(),
            datetime.strptime(rawdata['results']['sunrise'], '%I:%M:%S %p').time()).replace(tzinfo=pytz.utc)
        sunrise = sunrise_utc.astimezone(pytz.timezone(self.timezone))

        sunset_utc = datetime.combine(now_utc.date(),
            datetime.strptime(rawdata['results']['sunset'], '%I:%M:%S %p').time()).replace(tzinfo=pytz.utc)
        sunset = sunset_utc.astimezone(pytz.timezone(self.timezone))

        self.data["sunrise"] = sunrise.strftime('%Y-%m-%d %H:%M:%S')
        self.data["sunset"] = sunset.strftime('%Y-%m-%d %H:%M:%S')

        self.__save_Data()

        return True

    def __refresh(self):
        # Test if the local stored daylight data is set and up-to-date.
        # If not then call the Webservice to get new data.
        if(self.data["sunrise"] != ""):

            now = datetime.now()
            date = datetime.strptime(self.data["sunrise"], '%Y-%m-%d %H:%M:%S')

            if(date.date() != now.date()):
                self.__get_NewData()
        else:
            self.__get_NewData()

    @property
    def isSunUp(self):
        self.__refresh()

        now = datetime.now()

        sunrise = datetime.strptime(self.data["sunrise"], '%Y-%m-%d %H:%M:%S')
        sunset = datetime.strptime(self.data["sunset"], '%Y-%m-%d %H:%M:%S')

        self.logger.debug('Now: '+ now.strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.debug('Sunrise: ' + sunrise.strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.debug('Sunset: '+ sunset.strftime('%Y-%m-%d %H:%M:%S'))

        return now > sunrise and now < sunset

#if __name__ == "__main__":
#    prog = Daylight(config=None, logger=None)
#    print(prog.isSunUp)
