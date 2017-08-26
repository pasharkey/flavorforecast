"""Alexa Skill to look up the flavor forecast for The Diary Godmother."""

import sys
import logging
import datetime

from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

from dgm import api


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
forecast = DGMApi()


@ask.launch
def launch():
    """Start the skill."""
    greeting_text = render_template('greeting')
    reprompt_text = render_template('reprompt')
    return question(greeting_text).reprompt(reprompt_text)


@ask.intent('GetSearchDateIntent', convert={'date': 'date'})
def search_date(date):
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    # handle any date converrsion errors
    if 'date' in convert_errors:
        # since age failed to convert, it keeps its string
        # value (e.g. "?") for later interrogation.
        repeatdate_text = render_template('repeatdate')
        return question(repeatedate_text)
    if(not date):
        nodate_text = render_template('nodate')
        return question(nodate_text)

    result = forecast.search(date)
    print("Searching for the flavor of the day for: {}".format(date))
    return _search(result)


@ask.intent('GetSearchIntent')
def search():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    date = datetime.datetime.now()
    result = forecast.search(date)
    print("Searching for the flavor of the day for: {}".format(date))
    return _search(result)


def _search(result):
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    if(result.has_error):
        error_text = render_template(
            'searcherror', date=result.humanized_date)
        return question(error_text)
    elif(result.found):

        # if more than one result prepend `and` to each result
        if(result.size == 1):
            flavor_text = falvors[0]
        else:
            flavor_text = ('and ').join(falvors)

        found_text = render_template(
            'found', date=result.humanized_date, flavors=flavor_text)
        return statement(found_text)
    else:
        # check if store closed
        if(result.closed):
            # check if th date was for current day or past/future
            if(result.date == datetime.datetime.now()):
                closed_text = render_template(
                    'notfoundclosed', date=result.humanized_date, flavors=flavor_text)
                return statement(closed_text)
            elif(result.date > datetime.datetime.now())
                closed_text = render_template(
                    'notfoundclosedfuture', date=result.humanized_date, flavors=flavor_text)
                return statement(closed_text)
            else:
                closed_text = render_template(
                    'notfoundclosedpast', date=result.humanized_date, flavors=flavor_text)
                return statement(closed_text)
        else:
            notfound_text = render_template(
                'notfound', date=result.humanized_date)
            return statement(notfound_text)


@ask.intent('GetOpenIntent')
def open():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.open):
        opennow_text = render_template('opennow', answer='Yes', time=status.time_until)
        return statement(notfound_text)
    else:
        closednow_text = render_template('closednow', answer='No', time=status.time_until)
        return statement(closednow_text)


@ask.intent('GetOpenDateIntent', convert={'date': 'date'})
def open(date):
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    # handle any date converrsion errors
    if 'date' in convert_errors:
        # since age failed to convert, it keeps its string
        # value (e.g. "?") for later interrogation.
        return question("Can you please repeat the date?")
    if(not date):
        nodate_text = render_template('nodate')
        return question(nodate_text)

    status = forecast.get_status_on_date(date)
    if(status.open):

        # query for the hours on that day
        hours = forecast.operating_hours(date)
        openndate_text = render_template(
            'opendate', answer='Yes', date=hours.humanized_date, start=hours.open_str, end=hours.closed_str)
        return statement(openndate_text)
    else:
        closeddate_text = render_template(
            'closednowq', answer='No', date=status.humanized_date)
        return statement(closeddate_text)


@ask.intent('GetClosedIntnet')
def closed():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.open):
        opennow_text = render_template('opennowq', answer='No', time=status.time_until)
        return statement(notfound_text)
    else:
        closednow_text = render_template('closednowq', answer='Yes', time=status.time_until)
        return statement(closednow_text)

@ask.intent('GetClosedDateIntent')
def closed(date):
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    # handle any date converrsion errors
    if 'date' in convert_errors:
        # since age failed to convert, it keeps its string
        # value (e.g. "?") for later interrogation.
        return question("Can you please repeat the date?")
    if(not date):
        nodate_text = render_template('nodate')
        return question(nodate_text)

    status = forecast.get_status_on_date(date)
    if(status.open):

        # query for the hours on that day
        hours = forecast.operating_hours(date)
        openndate_text = render_template(
            'opendate', answer='No', date=hours.humanized_date, start=hours.open_str, end=hours.closed_str)
        return statement(openndate_text)
    else:
        closeddate_text = render_template(
            'closednowq', answer='Yes', date=status.humanized_date)
        return statement(closeddate_text)


@ask.intent('GetHoursIntent')
def hours():

    date = datetime.datetime.now()
    hours = forecast.operating_hours(date)
    hours_text = render_template(
            'hours', date=hours.humanized_date, start=hours.open_str, end=hours.closed_str)
    return statement(openndate_text)


@ask.intent('GetHoursForDayIntent', convert={'date': 'date'})
    
    # handle any date converrsion errors
    if 'date' in convert_errors:
        # since age failed to convert, it keeps its string
        # value (e.g. "?") for later interrogation.
        return question("Can you please repeat the date?")
    if(not date):
        nodate_text = render_template('nodate')
        return question(nodate_text)

    hours = forecast.operating_hours(date)
    hours_text = render_template(
            'hours', date=hours.humanized_date, start=hours.open_str, end=hours.closed_str)
    return statement(openndate_text)


@ask.intent('GetTimeUntilOpenIntent')
def timeuntilopen():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.open):
        opennow_text = render_template('opennow', time=status.time_until)
        return statement(opennow_text)
    else:
        timetoopen_text = render_template('timeuntilopen', time=status.time_until)
        return statement(timetoopen_text)

@ask.intent('GetTimeUntilCloseIntent')
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.open):
        closednow_text = render_template('closednow', time=status.time_until)
        return statement(closednow_text)
    else:
        timetoclose_text = render_template('timeuntilclose', time=status.time_until)
        return statement(timetoclose_text)


@ask.intent('GetLocationIntent')
def location():
    location_text = render_template('location')
    return statement(location_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    """Give the user the help text."""
    help_text = render_template('reprompt')
    return question(help_text).reprompt(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    """Allow the user to stop interacting."""
    return statement("Goodbye")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    """Allow the user to cancel the interaction."""
    return statement("Goodbye")


@ask.session_ended
def session_ended():
    """End the session gracefully."""
    return "", 200


def main():
    """Utility method to run the app if outside of lambda."""
    app.run()


if __name__ == '__main__':
    main()
