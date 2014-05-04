"""Authorization/authentication of a
user. Will then get the user's watchlist and list of
funds."""
import requests
import random
import simplejson as json
from flask import (request, redirect, session, url_for,
                   render_template, jsonify, flash)
from jivedata.webapp import app


def make_user_request(endpoint, data=None):
    """Make a request to the Jive Data API. Will first refresh the token, then
    use the new access token"""
    params = {'grant_type': 'refresh_token',
              'client_id': app.config['secondary_client_id'],
              'client_secret': app.config['secondary_client_secret'],
              'refresh_token': session['user_oauth_token']['refresh_token']}

    url = 'https://api.jivedata.com/oauth/token/'
    response = requests.get(url, params=params, verify=False)
    session['user_oauth_token'] = response.json()
    headers = {'Authorization': 'Bearer %s' %
               session['user_oauth_token']['access_token']}

    url = 'https://api.jivedata.com/' + endpoint
    if data is not None:
        return requests.post(url, data=data, headers=headers, verify=False)
    else:
        return requests.get(url, headers=headers, verify=False)


@app.route('/logout/')
def logout():
    """Logout the user and return them to /filings/"""
    if 'user_oauth_token' in session:
        del session['user_oauth_token']
    if 'user_oauth_state' in session:
        del session['user_oauth_state']
    if 'watchlist' in session:
        del session['watchlist']
    if 'watchlist_ciks' in session:
        del session['watchlist_ciks']
    if 'funds' in session:
        del session['funds']
    if 'funds_ciks' in session:
        del session['funds_ciks']
    return redirect(url_for('filings'))


@app.route('/login/')
def login():
    """Login the user to the Jive Data API"""
    if 'user_oauth_token' in session:
        del session['user_oauth_token']

    rand = random.SystemRandom()
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    state = ''.join(rand.choice(chars) for _ in range(30))
    session['user_oauth_state'] = state
    auth_url = ('https://api.jivedata.com/oauth/authorize/'
                '?response_type=code&client_id=%s&state=%s' %
                (app.config['secondary_client_id'],
                 session['user_oauth_state'])
                )
    return redirect(auth_url)


@app.route('/authorized/')
def authorized():
    """The registered callback"""
    if request.args.get('state') == session['user_oauth_state']:
        params = {'client_id': app.config['secondary_client_id'],
                  'client_secret': app.config['secondary_client_secret'],
                  'code': request.args.get('code')}
        params['grant_type'] = 'authorization_code'
        params['redirect_uri'] = app.config['redirect_uri']
        response = requests.get('https://api.jivedata.com/oauth/token/',
                                params=params, verify=False)
        token = response.json()
        flash('You are logged in', 'info')
        session['user_oauth_token'] = token
        return redirect(url_for('user_details'))
    return 'State variable does not match'


@app.route('/me/')
def user_details():
    """Display the user's watchlist and funds list"""
    if 'user_oauth_token' not in session or \
        'refresh_token' not in session['user_oauth_token']:
        return redirect('/login/')

    get_watchlist()
    return render_template('me.jinja2')


@app.route('/update/')
def update():
    """Update the user's watchlist or funds list"""
    try:
        params = json.loads(request.args.get('params'))
    except TypeError:
        params = {}

    if params['action'] == 'add':
        if params['item'] == 'watchlist':
            params['cik'] = int(session['ticker']['cik'])
        elif params['item'] == 'funds':
            params['cik'] = int(session['fund']['cik'])

    response = make_user_request('/user/update/', data=params)
    if response is None or '_error_' in response.text:
        return jsonify(_message_=response.text)

    get_watchlist()
    return jsonify(_message_='Success')


def get_watchlist():
    """Get the user's watchlist & funds list and save them
    in the session"""
    try:
        """ if the user deletes an item then quickly refreshes the page it
        messes up the token stuff and results in a KeyError"""
        response = make_user_request('/user/detail/')
        results = response.json()

        if '_results_' in results:
            if 'funds' in results['_results_']:
                session['funds'] = results['_results_']['funds']
                session['funds_ciks'] = [x['cik'] for x in session['funds']]
            if 'watchlist' in results['_results_']:
                watchlist = results['_results_']['watchlist']
                for row in watchlist:
                    if row['ticker'] == '':
                        row['ticker'] = '--'
                session['watchlist'] = watchlist
                session['watchlist_ciks'] = [x['cik'] for x in
                                             session['watchlist']]

    except KeyError:
        pass

    return
