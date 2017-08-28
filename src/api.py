"""Interact with The Diary Godmother webpage."""
import datetime
import requests
import time_util
import humanize
import pytz
from collections import namedtuple
from dateutil import tz

from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


def _build_params(dt):
    """Takes a date and builds the parameters needed to scrape the dgm website.

    :param dt: the `datetime` object
    :returns: the `params` that contain the needed api information
    """
    params = (('yr', dt.year),
              ('month', dt.month),
              ('dy', dt.day),
              ('cid', 'mc-0191cbfb6d82b4fdb92b8847a2046366'))
    return params


def _build_flavor_forecast(flavors, dt):
    """Takes the flavors array and the searched date and builds a result object
    with containing the flavor forecast information

    :param flavors: the array of flavors
    :param dt: the `datetime` object
    :returns: a `Result `namedtuple` holding the results

    """

    # check the lengh and build the `Result` object
    if len(flavors) < 1:
        return _build_result(False, None, dt, 0, False, False, None)
    elif len(flavors) == 1:
        return _build_result(True, flavors, dt, 1, False, False, None)
    else:
        return _build_result(True, flavors, dt, len(flavors), False, False, None)


def _is_closed(dt):
    """Takes a date and determines if the dairy godmother is closed at that time

    :param dt_obj: the `datetime` object
    :returns: a `Status `namedtuple` holding the open or closed status of the store

    """
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
    if((dt.isoweekday() in [1, 4, 5, 6, 7]) and (dt.hour in range(2, 16))):
        return _build_status(False, True, dt, False, None)
    elif((dt.isoweekday() in [2, 3]) and (dt.hour in range(1, 16))):
        return _build_status(False, True, dt, False, None)
    else:
        return _build_status(True, False, dt, False, None)


def _seconds_until_open(dt):
    """Takes a date and calculates the number of seconds until the dairy godmother
    opens

    :param date: the date to calculate against
    :returns: the number of seconds until the dairy godmother opens

    """
    dt_open = time_util.build_time(dt.year, dt.month, dt.day, 16, 00, 00)
    return (dt_open - dt).seconds


def _seconds_until_close(dt):
    """Takes a date and calculates the number of seconds until the dairy godmother
    closes

    :param date: the date to calculate against
    :returns: the number of seconds until the dairy godmother closes

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


def _build_result(found, flavors, date, size, closed, has_error, error):
    """Takes a date and calculates the number of seconds until the dairy godmother
    closes

    :param date: the date to calculate against
    :returns: the number of seconds until the dairy godmother closes

    """
    return Result(found=found, flavors=flavors, date=date, humanized_date=humanize.naturaldate(date),
                  size=size, closed=closed, has_error=has_error, error=error)


def _build_status(is_open, is_closed, date, has_error, error):
    """Takes a date and calculates the number of seconds until the dairy godmother
    closes

    :param date: the date to calculate against
    :returns: the number of seconds until the dairy godmother closes

    """
    if(is_open):
        return Status(is_open=is_open, is_closed=is_closed, date=date, humanized_date=humanize.naturaldate(date),
                  time_left=time_util.humanize_time(_seconds_until_close(date)), has_error=has_error, error=error)
    else:
        return Status(is_open=is_open, is_closed=is_closed, date=date, humanized_date=humanize.naturaldate(date),
                  time_left=time_util.humanize_time(_seconds_until_open(date)), has_error=has_error, error=error)


def _build_hours(open_str, close_str, date):
    """Takes a date and calculates the number of seconds until the dairy godmother
    closes

    :param date: the date to calculate against
    :returns: the number of seconds until the dairy godmother closes

    """
    return Hours(open_str=open_str, close_str=close_str, date=date, humanized_date=humanize.naturaldate(date))

# Create objects to store the results for a search and the status of the
# store being open or closed
Result = namedtuple('Result', [
                    'found', 'flavors', 'date', 'humanized_date', 'size', 'closed', 'has_error', 'error'])
Status = namedtuple('Status', ['is_open', 'is_closed',
                               'date', 'humanized_date', 'time_left', 'has_error', 'error'])
Hours = namedtuple('Hours', ['open_str', 'close_str', 'date', 'humanized_date'])


class DGMApi(object):
    """Class to facilitate interaction."""

    def __init__(self):
        """Initialize the url.

        :returns: `None`
        """
        self.url = 'http://www.TheDairyGodmother.com/flavor-of-the-day-forecast/'

    def operating_hours(self, dt):
        """Takes a date and determines the operating hours of the store

        :param dt: the `datetime` to check store hours for
        :returns: a `Hours` `namedtuple` with hours information

        """
        if dt.isoweekday() in range(1, 2):
            return _build_hours('12 PM', '10 PM', dt)
        else:
            return _build_hours('12 PM', '11 PM', dt)

    def get_status(self):
        """Determines if the store is currently closed

        :returns: a `Status `namedtuple` holding the open or closed status of the store

        """
        dt = time_util.now()
        return _is_closed(dt)

    def get_status_on_date(self, dt):
        """Determines if the store is currently closed

        :param dt: the `datetime` to check status for
        :returns: a `Status `namedtuple` holding the open or closed status of the store

        """
        return _is_closed(dt)

    def search(self, dt):
        """Search the flavor of the day based on the date

        :param dt: the `datetime` to search for
        :returns: a `Result `namedtuple` holding the flavor forecast results

        """

        # perform search based on the passed in date
        try:
            print("Searching for flavor of the day for {}".format(dt))

            # build the params to scrap dgm webpage
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
                    flavors.append((summary.text.split('-')[0].split('(')[0]).strip())

                # make sure the strings are encoded 
                flavors = [x.encode('UTF8') for x in flavors]

                # ensure that it is not closed on this day
                if any('closed' in f.lower() for f in flavors):
                    return _build_result(False, None, dt, 0, True, False, None)

                # build the flavor forecast result
                return _build_flavor_forecast(flavors, dt)

            # check for no results or html error
            elif len(results) < 1:
                return _build_result(False, None, dt, 0, False, False, None)
            else:
                return _build_result(False, None, dt, 0, False, True,
                    'More than one table cell event summary with id of calendar-' + 
                       time_util.stringify_date(dt) + 'found.')
        except:
            return _build_result(False, None, dt, 0, False, True,
                    'An exception occured when performing a flavor forecast search.')
