from jinja2 import filters
from jivedata.webapp import app
from jivedata.utils import (avg_price, current_est, format_aum, format_number,
                            format_shares, format_value, insider_position,
                            pretty_date, pretty_date_time, truncator,
                            prior_wording)


def current_year(*args):
    """Return the current year"""
    return current_est().year


def format_blanks(val):
    """Make blank values apparent to the end-user"""
    if val == '':
        val = '--'
    return val


def list_to_set(l):
    """Convert list to set. Allows us to check if all
    the values in a list are blanks"""
    return list(set([x['value'] for x in l]))


def format_currency(value):
    """Format a currency, putting negative signs before dollar-sign"""
    formatted = "${:,d}".format(abs(int(value)))
    if int(value) < 0:
        formatted = "-%s" % formatted
    return formatted


def format_per_share_currency(value):
    """Format per-share currency, putting negative signs before dollar-sign"""
    try:
        formatted = "${0:,.2f}".format(abs(float(value)))
        if float(value) < 0:
            formatted = "-%s" % formatted
    except:
        formatted = '--'
    return formatted


def per_share(num, denominator):
    try:
        return float(num) / float(denominator)
    except:
        return '--'


def format_percentage(value):
    try:
        return "{0:.1f}%".format(float(value) * 100)
    except:
        return '--'


# econ filters
def frequency_long(frequency_short):
    """Convert short frequency to a human-readable version"""
    frequency = ''
    if frequency_short == 'A':
        frequency = 'Annual'
    elif frequency_short == 'SA':
        frequency = 'Semi-Annual'
    elif frequency_short == 'Q':
        frequency = 'Quarterly'
    elif frequency_short == 'M':
        frequency = 'Monthly'
    elif frequency_short == 'BW':
        frequency = 'Bi-Weekly'
    elif frequency_short == 'W':
        frequency = 'Weekly'
    elif frequency_short == 'D':
        frequency = 'Daily'
    return frequency


filters.FILTERS['avg_price'] = avg_price
app.jinja_env.filters['current_year'] = current_year
filters.FILTERS['format_aum'] = format_aum
filters.FILTERS['format_blanks'] = format_blanks
app.jinja_env.filters['format_blanks'] = format_blanks
filters.FILTERS['format_currency'] = format_currency
filters.FILTERS['format_per_share_currency'] = format_per_share_currency
filters.FILTERS['format_number'] = format_number
filters.FILTERS['format_percentage'] = format_percentage
filters.FILTERS['format_shares'] = format_shares
filters.FILTERS['format_value'] = format_value
filters.FILTERS['frequency_long'] = frequency_long
filters.FILTERS['insider_position'] = insider_position
filters.FILTERS['list_to_set'] = list_to_set
filters.FILTERS['per_share'] = per_share
filters.FILTERS['pretty_date'] = pretty_date
app.jinja_env.filters['pretty_date'] = pretty_date
filters.FILTERS['pretty_date_time'] = pretty_date_time
filters.FILTERS['prior_wording'] = prior_wording
filters.FILTERS['truncator'] = truncator
