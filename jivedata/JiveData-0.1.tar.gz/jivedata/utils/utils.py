import pytz
from datetime import datetime
import dateutil.parser
from math import fabs


def truncator(name, chars):
    """Shortens a name to chars and replaces '|' with a comma
    and gets rid of leading and trailing spaces"""
    name = ' '.join(name.split())
    truncated_name = (name[:chars] + '...') if len(name) > chars else name
    return truncated_name.replace('|', ', ')


def string_to_eastern_datetime(s):
    """Converts a date string to timezone-aware datetime format"""
    utc = dateutil.parser.parse(s)
    eastern = pytz.timezone('US/Eastern')
    utc = utc.replace(tzinfo=None)
    return eastern.localize(utc)


def date_time_to_string(d):
    """Converts a datetime to "Apr 7, 2014 2:51PM" format,
    removing leading zeroes from the day and hour"""
    day = d.strftime('%d').lstrip('0')
    month = d.strftime('%b')
    year = d.strftime('%Y')
    full_date = "%s %s, %s" % (month, day, year)
    full_time = d.strftime('%I:%M%p').lstrip('0')
    return '%s %s' % (full_date, full_time)


def current_est():
    """Gets the current EST date time"""
    now_utc = pytz.utc.localize(datetime.utcnow())
    return now_utc.astimezone(pytz.timezone('US/Eastern'))


def pretty_date_time(d):
    """Converts a string to a pretty datetime, complete
    with minutes filed from now. Results in something like
                Apr 8, 2014 5:34PM
                (34 minutes ago)
    """
    filing_date_est = string_to_eastern_datetime(d)
    now_est = current_est()
    delta = (now_est - filing_date_est).total_seconds()
    filing_date_string = date_time_to_string(filing_date_est)
    formatted = """<span id="long_date">%s</span><span id="short_date_break">
                <br></span><span id="short_date"><span id="l_paren">(</span>%s
                <span id="r_paren">)</span></span>"""

    if delta > 3600:
        return filing_date_string
    if delta < 60:  # if filed less than 1 minute ago
        pritty = 'just now'
    if delta < 60 * 1.5:  # if filed less than 1.5 minutes ago
        pritty = 'a minute ago'
    if delta < 3600:  # if filed less than 1 hour ago
        diff = "%.0f" % (delta / 60)
        pritty = '%s minutes ago' % (diff)
    return formatted % (filing_date_string, pritty)


def pretty_date(d):
    """Like pretty_date_time, but without the time.
    Accepts a string. Results in something like
                     6/30/2014
    """
    d = dateutil.parser.parse(d)
    day = d.strftime('%d').lstrip('0')
    month = d.strftime('%b')
    year = d.strftime('%Y')
    full_date = "%s %s, %s" % (month, day, year)
    return full_date


# insiders
def insider_position(insider):
    position = ''
    if insider['is_officer'] != 0:
        position = insider['is_officer']
    if insider['is_director'] == 1:
        position = "Director, %s" % (position)
    if insider['is_ten_percent_owner'] != 0:
        position = "%s owner, %s" % ('10%', position)
    position = truncator(str(position).rstrip().rstrip(','), 40)
    return position


def format_value(v):
    return '${0:,.0f}'.format(v)


def format_shares(s):
    try:
        return '{0:,.0f}'.format(s)
    except:
        return ''


def avg_price(v, s):
    try:
        return'${0:,.2f}'.format(fabs(float(v / s)))
    except:
        return ''


# econ
def prior_wording(frequency_short):
    """Create the comparison wording for the prior period based
    off the frequency_short"""
    prior_wording = ''
    if frequency_short == 'A':
        prior_wording = 'Last yr'
    elif frequency_short == 'SA':
        prior_wording = '6 months ago'
    elif frequency_short == 'Q':
        prior_wording = 'Last quarter'
    elif frequency_short == 'M':
        prior_wording = 'Last month'
    elif frequency_short == 'BW':
        prior_wording = '2 wks ago'
    elif frequency_short == 'W':
        prior_wording = 'Last week'
    elif frequency_short == 'D':
        prior_wording = 'Previous day'
    return prior_wording


# 13F filings
def format_aum(value):
    """Format the AUM"""
    units = ''
    value = float(value)
    if value < 1000000000:
        # Don't make it into trillions as they probably made a mistake??
        value = value * 1000
    if value >= 1000000 and value < 1000000000:
        value = value / 1000000
        units = 'M'
    elif value >= 1000000000:
        value = value / 1000000000
        units = 'B'
    formatted = '${:,.1f}'.format(abs(value))
    if value < 0:
        formatted = "-%s" % formatted
    return formatted + units


def format_number(value):
    return "{:,d}".format(int(value))
