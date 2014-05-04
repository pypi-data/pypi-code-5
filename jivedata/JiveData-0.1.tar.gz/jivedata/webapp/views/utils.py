from flask import request, session, jsonify, render_template
from jivedata.webapp import app
import simplejson as json
from jivedata.utils import Client


def make_api_request(endpoint, params={}, headers={}):
    """A handler to make api requests to api.jivedata.com. For test
    data, if the endpoint is a /list/ change it to /new/ and if the endpoint
    is /detail/ then set the 'test' parameter"""

    if app.config['test_data'] == True:
        if endpoint in ['/filings/list/', '/insiders/list/',
                        '/13F/list/', '/econ/list/']:
            endpoint = endpoint.replace('/list/', '/new/')
        elif endpoint in ['/financials/detail/', '/econ/detail/',
                          '/13F/detail/']:
            params['test'] = True
    client = Client(client_id=app.config['client_id'],
                    client_secret=app.config['client_secret'])

    client.get_protected(endpoint=endpoint, params=params)
    return client.results


@app.route('/ticker/')
def ticker():
    """Ticker Autocomplete """
    params = {'term': request.args.get('term'), 'number': 10}
    response = make_api_request('/tickers/search/', params)
    return jsonify(results=response['_results_'])


def store_cik(cik):
    """
    Save cik or ticker parameter to a session variable.
    Applies to Financials, Filings and Insiders
    """
    nonnumeric = None
    params = {'number': 10}
    try:
        params['cik'] = int(cik)
    except:
        params['term'] = cik.upper()
        nonnumeric = True

    response = make_api_request('/tickers/search/', params)
    tickers = response['_results_']
    if nonnumeric is not None:
        # a search by "term" has the potential to return > 1 result
        tickers = [x for x in tickers if x['ticker'] == params['term']]

    session['ticker'] = {}
    if len(tickers) == 1:
        session['watchlist_view'] = 'false'
        session['ticker'] = {'cik': tickers[0]['cik'],
                             'ticker': tickers[0]['ticker'],
                             'name': tickers[0]['name']}
    return


def default_watchlist():
    """If they click "Watchlist View" but are not logged in
    give them a default watchlist"""
    return ','.join(['1288776', '1018724', '1065280', '1467858'])


def default_funds():
    """If they click "My Funds" but are not logged in
    give them a default funds list"""
    return ','.join(['1061768', '1420192', '921669', '1061165', '934639'])


@app.route('/update_settings/')
def update_settings():
    """
    Store the user settings in a session (e.g. if they change tickers,
    check/uncheck watchlist view, most viewed, etc). These are all set
    via jQuery/Ajax.
    """
    if request.is_xhr:
        if 'ticker' in request.args:
            session['ticker'] = json.loads(request.args.get('ticker'))
            session['watchlist_view'] = 'false'

        if 'watchlist_view' in request.args:
            session['watchlist_view'] = request.args.get('watchlist_view')
            session['ticker'] = {}

        # filings settings
        if 'forms' in request.args:
            session['forms'] = request.args.get('forms')
            if request.args.get('forms') != '0':
                session['insiders'] = 'false'

        if 'insiders' in request.args:
            session['insiders'] = request.args.get('insiders')

        # insider settings
        if 'planned' in request.args:
            session['planned'] = request.args.get('planned')

        # 13F settings
        if 'my_funds_view' in request.args:
            session['my_funds_view'] = request.args.get('my_funds_view')
            session['fund'] = ''

        if 'fund' in request.args:
            session['fund'] = request.args.get('fund')
            session['my_funds_view'] = 'false'

        # econ settings
        if 'most_viewed' in request.args:
            session['most_viewed'] = request.args.get('most_viewed')

        if 'series' in request.args:
            session['series'] = request.args.get('series')

        return jsonify(result='success')
    return jsonify(error='Could not update...')
