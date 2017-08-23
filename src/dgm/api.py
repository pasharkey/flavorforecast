"""Interact with The Diary Godmother webpage."""
import datetime
import requests
import response
import time_util
import humanize
import pytz
from dateutil import tz

from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


def _build_params(dt_obj):
    """Parse the date string from the database intoa `datetime` object.

    :param date_string: the raw date string to parse
    :returns: the `datetime` version of the given date string
    """
    params = (('yr', dt_obj.year),
              ('month', dt_obj.month),
              ('dy', dt_obj.day),
              ('cid', 'mc-0191cbfb6d82b4fdb92b8847a2046366'))
    return params


def _build_flavor_forecast(flavors, dt_obj):
    """Takes a date and checks the flavor forecast for that date

    :param date: the string date passed from Alexa
    :returns: the speech output of the flavor or errors for the date requested

    """

    # declare the speech output as error in case it does not get updated
    forecast = response.msg.get(300)

    if len(flavors) < 1:
        forecast = response.msg.get(101).format(humanize.naturaldate(dt_obj))
    elif len(flavors) == 1:
        forecast = response.msg.get(200).format(
            humanize.naturaldate(dt_obj), flavors[0])
    else:
        forecast = response.msg.get(200).format(
            humanize.naturaldate(dt_obj), (' and '.join(flavors)))

    return forecast


def _is_closed(dt):
    '''
    All dates are converted to UTC to remove any local or native timestamps
    due to where the skill is being run. 

    EST Store hours: M-T 12:00pm-21:00pm, W-Th-F-S-Su 12:00pm-22:00pm
    UTC Store hours: M  00:00 - 02:00, 16:00 - 24:00
                     T  00:00 - 01:00, 16:00 - 24:00
                     W  00:00 - 01:00, 16:00 - 24:00
                     Th 00:00 - 02:00, 16:00 - 24:00
                     Fr 00:00 - 02:00, 16:00 - 24:00
                     S  00:00 - 02:00, 16:00 - 24:00 
                     Su 00:00 - 02:00, 16:00 - 24:00
    '''

    # declare the tuple that will store the information
    status_tuple = ()

    if((dt.isoweekday() in [1, 4, 5, 6, 7]) and (dt.hour in range(2, 16))):
        status_tuple = (True, time_util.humanize_time(_seconds_until_open(dt)))
    elif((dt.isoweekday() in [2, 3]) and (dt.hour in range(1, 16))):
        status_tuple = (True, time_util.humanize_time(_seconds_until_open(dt)))
    else:
        status_tuple = (False, time_util.humanize_time(
            _seconds_until_close(dt)))

    return status_tuple


def _seconds_until_open(dt):
    """Takes a date and checks the flavor forecast for that date

    :param date: the string date passed from Alexa
    :returns: the speech output of the flavor or errors for the date requested

    """
    dt_open = time_util.build_time(dt.year, dt.month, dt.day, 16, 00, 00)
    return (dt_open - dt).seconds


def _seconds_until_close(dt):
    """Takes a date and checks the flavor forecast for that date

    :param date: the string date passed from Alexa
    :returns: the speech output of the flavor or errors for the date requested

    """
    if((dt.isoweekday() in [1, 2]) and (dt.hour in range(16, 24))):
        dt_close = time_util.build_time(dt.year, dt.month, dt.day + 1, 01, 00, 00)
        return (dt_close - dt).seconds
    elif((dt.isoweekday() in [1, 2]) and (dt.hour in range(0, 1))):
        dt_close = time_util.build_time(dt.year, dt.month, dt.day, 01, 00, 00)
        return (dt_close - dt).seconds
    elif((dt.isoweekday() in [3, 4, 5, 6, 7]) and (dt.hour in range(16, 24))):
        dt_close = time_util.build_time(
            dt.year, dt.month, dt.day + 1, 2, 00, 00)
        return (dt_close - dt).seconds
    elif((dt.isoweekday() in [3, 4, 5, 6, 7]) and (dt.hour in range(0, 2))):
        dt_close = time_util.build_time(dt.year, dt.month, dt.day, 02, 00, 00)
        return (dt_close - dt).seconds


class DGMApi(object):
    """Class to facilitate interaction."""

    def __init__(self):
        """Initialize the url.

        :returns: `None`
        """
        self.url = 'http://www.TheDairyGodmother.com/flavor-of-the-day-forecast/'

    def operating_hours(self, raw_date):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        dt = time_util.parse_date(raw_date)

        if dt.isoweekday() in range(1, 2):
            return response.msg.get(403).format(humanize.naturaldate(dt))
        else:
            return response.msg.get(404).format(humanize.naturaldate(dt))

    def open_now(self):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        dt = time_util.now()

        # check if open now
        result = _is_closed(dt)
        if(not result[0]):
            return "Yes, " + response.msg.get(401).format(result[1])
        else:
            return "No, " + response.msg.get(402).format(result[1])

    def closed_now(self):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        dt = time_util.now()

        # check if open now
        result = _is_closed(dt)
        if(result[0]):
            return "Yes, " + response.msg.get(402).format(result[1])
        else:
            return "No, " + response.msg.get(401).format(result[1])

    def time_until_open(self):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        dt = time_util.now()
        result = _is_closed(dt)

        if(result[0]):
            return response.msg.get(400).format(result[1])
        else:
            return response.msg.get(401).format(result[1])

    def time_until_closed(self):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        dt = time_util.now()
        result = _is_closed(dt)

        if(not result[0]):
            return response.msg.get(401).format(result[1])
        else:
            return response.msg.get(400).format(result[1])

    def location(self):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """
        return response.msg.get(500)

    def search(self, raw_date):
        """Search the API for the given title.

        :param raw_title: the raw spoken title string to search four
        :returns: the best match from the API given the params

        """

        # perform search based on the passed in raw_date
        try:
            print("Searching for flavor of the day for {}".format(raw_date))

            # create date objects and build params
            dt = time_util.parse_date(raw_date, True)

            params = _build_params(dt)

            req = requests.get(self.url, params=params)

            print("sending request to {}".format(req.url))

            soup = BeautifulSoup(req.text, 'html.parser')

            # find the <td> with the specified date
            results = soup.find_all(
                'td', attrs={'id': 'calendar-' + time_util.stringify_date(dt)})

            # find the all of the event-title-summary for that day
            if len(results) == 1:
                event_summary = results[0].find(
                    'h3', attrs={'class': 'event-title summary'}).find_all('a')

                # create list to store clean flavors
                flavors = []

                # clean up the summary
                for summary in event_summary:
                    flavors.append(summary.text.split('-')[0].split('(')[0])

                # ensure that it is not closed on this day
                if any('closed' in f.lower() for f in flavors):
                    return response.msg.get(100)

                return _build_flavor_forecast(flavors, dt)

            else:
                return response.msg.get(101).format(humanize.naturaldate(dt))

        except ValueError:
            return response.msg.get(300)

        return response.msg.get(300)
