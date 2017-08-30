"""Alexa Skill to look up the flavor forecast for The Diary Godmother."""

import sys
import logging
import datetime

from flask import Flask, render_template
from flask_ask import Ask, statement, question, convert_errors, session

import api


app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)
forecast = api.DGMApi()


@ask.launch
def launch():
    """Start the skill."""
    greeting_text = render_template('greeting')
    reprompt_text = render_template('reprompt')
    return question(greeting_text).reprompt(reprompt_text)


@ask.intent('GetSearchDateIntent', convert={'date': 'date'})
def search_date(date):
    """The default intent to be triggered. Uses the date to search the DGM API.
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
    """The search for current day intent to be triggered. Uses the title to search 
    the DGM API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    date = datetime.datetime.now()
    result = forecast.search(date)
    print("Searching for the flavor of the day for: {}".format(date))
    return _search(result)


def _search(result):
    """Helper method for both the `GetSearchDateIntent` and the `GetSearchIntent`. 
    Will take the search results and format them into an appropriate `flask-ask.statement`.
    :returns: a `flask-ask.statement` result with the given template text
    """

    if(result.has_error):
        error_text = render_template(
            'searcherror', date=result.humanized_date)
        return question(error_text)
    elif(result.found):

        # if more than one result prepend `and` to each result
        if(result.size == 1):
            flavor_text = result.flavors[0]
        else:
            flavor_text = ('and ').join(result.flavors)

        found_text = render_template(
            'found', date=result.date, flavors=flavor_text)
        return statement(found_text)
    else:
        # check if store closed
        if(result.closed):
            print 'Result: ', result
            closed_text = render_template('notfoundclosed', date=result.date)
            return statement(closed_text)
        else:
            notfound_text = render_template('notfound', date=result.date)
            return statement(notfound_text)


@ask.intent('GetOpenIntent')
def open():
    """Determines if The Diary Godmother is open or not based on the current time.
    Method also returns the time left until open or the time left until close
    based on the status.
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.is_open):
        opennow_text = render_template('opennow', time=status.time_left)
        return statement(opennow_text)
    else:
        closednow_text = render_template('closednow', time=status.time_left)
        return statement(closednow_text)


@ask.intent('GetClosedIntent')
def closed():
    """Determines if The Diary Godmother is closed or not based on the current time.
    Method also returns the time left until open or the time left until close
    based on the status.
    :returns: a `flask-ask.statement` result with the given template text
    """
    status = forecast.get_status()

    # check if open
    if(status.is_open):
        opennow_text = render_template('opennow', time=status.time_left)
        return statement(opennow_text)
    else:
        closednow_text = render_template('closednow', time=status.time_left)
        return statement(closednow_text)


@ask.intent('GetOpenDateIntent', convert={'date': 'date'})
def open_date(date):
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

    # query to ensure was not randomly closed
    result = forecast.search(date)

    if(result.closed):
        closeddate_text = render_template('closeddate',  date=date)
        return statement(closeddate_text)

    else:
        # query for the hours on that day
        hours = forecast.operating_hours(date)
        openndate_text = render_template(
            'opendate', date=date, start=hours.open_str, end=hours.close_str)
        return statement(openndate_text)


@ask.intent('GetHoursIntent')
def hours():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    hours_text = render_template('hours')
    return statement(hours_text)


@ask.intent('GetLocationIntent')
def location():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """
    location_text = render_template('location')
    return statement(location_text)


@ask.intent('GetAboutIntent')
def hours():
    """The default intent to be triggered. Uses the title to search the GB API.
    :param date: the date to search for the flavor of the day
    :returns: a `flask-ask.statement` result with the given template text
    """

    about_text = render_template('about')
    return statement(about_text)


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
