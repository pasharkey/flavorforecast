import calendar
import datetime
import time
import pytz

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
ALEXA_TIME_FORMAT = '%Y-%m-%d'


def parse_date(dt_string, alexa=False):
    """Parse the date string from the database into a `datetime` object.

    :param date_string: the raw date string to parse
    :returns: the `datetime` version of the given date string
    """
    if(alexa):
        return datetime.datetime.strptime(dt_string, ALEXA_TIME_FORMAT).replace(tzinfo=pytz.utc)
    else:
        return datetime.datetime.strptime(dt_string, TIME_FORMAT).replace(tzinfo=pytz.utc)

def now():
    """Parse the date string from the database into a `datetime` object.

    :param date_string: the raw date string to parse
    :returns: the `datetime` version of the given date string
    """
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def stringify_date(dt_obj):
    """Parse the date string from the database into a `datetime` object.

    :param date_string: the raw date string to parse
    :returns: the `datetime` version of the given date string
    """
    return dt_obj.strftime(ALEXA_TIME_FORMAT)

# Gets local time in given format
def get_current_local_time():
    local = datetime.datetime.now()
    return local.strftime(TIME_FORMAT)


# Gets UTC time in given format
def get_current_utc_time():
    utc = datetime.datetime.utcnow()
    return utc.strftime(TIME_FORMAT)


# Converts local time to UTC time
def local_2_utc():
    local = datetime.datetime.now().strftime(TIME_FORMAT)
    timestamp = str(time.mktime(datetime.datetime.strptime(
        local, TIME_FORMAT).timetuple()))[:-2]
    utc = datetime.datetime.utcfromtimestamp(int(timestamp))
    return utc


# Converts UTC time to local time
def utc_2_local():
    utc = datetime.datetime.utcnow().strftime(TIME_FORMAT)
    timestamp = calendar.timegm(
        (datetime.datetime.strptime(utc, TIME_FORMAT)).timetuple())
    local = datetime.datetime.fromtimestamp(timestamp).strftime(TIME_FORMAT)
    return local

# Converts the time object to UTC (must be in TIME_FORMAT)


def local_2_utc(dt_string):
    timestamp = str(time.mktime(datetime.datetime.strptime(
        dt_string, TIME_FORMAT).timetuple()))[:-2]
    utc = datetime.datetime.utcfromtimestamp(int(timestamp))
    return utc


def build_time(year, month, day, hours, seconds, minutes):
    return datetime.datetime(year, month, day, hours, seconds, minutes, 0, tzinfo=pytz.utc)

# builds humanized representation of the time based on seconds


def humanize_time(seconds, granularity=2):
    """Parse the date string from the database into a `datetime` object.

    :param date_string: the raw date string to parse
    :returns: the `datetime` version of the given date string
    """
    
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))

    if len(result) == 1:
        return result[0]
    elif len(result) == 2:
        return result[0] + ' and ' + result[1]
    elif len(result) == 3:
        return result[0] + ', ' + result[1] + ' and ' + result[2]
    elif len(result) == 4:
        return result[0] + ', ' + result[1] + ', ' + result[2] + ' and ' + result[3]
    elif len(result) == 5:
        return result[0] + ', ' + result[1] + ', ' + result[2] + ', ' + result[3] + ' and ' + result[4]
    else:
        return None

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)
