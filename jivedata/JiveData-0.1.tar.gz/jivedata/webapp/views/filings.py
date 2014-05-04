from flask import request, session, jsonify, render_template, redirect, flash
from jinja2 import Template
from jivedata.webapp import app
from jivedata.webapp.views.utils import (make_api_request,
                                         store_cik, default_watchlist)


@app.route('/filings/', defaults={'cik': None})
@app.route('/filings/<cik>/')
def filings(cik):
    """Filings list view"""
    if cik is None and 'ticker' in session and session['ticker'] != {}:
        cik = session['ticker']['cik']

    if cik is not None:
        store_cik(cik)
        if session['ticker'] == {}:  # if ticker is invalid
            flash('Invalid ticker', 'danger')
            return redirect('/filings/')

    params = {}
    try:
        page = int(request.args.get('page'))
    except:
        page = None
    if page != None:
        params['page'] = page

    try:
        params['forms'] = session['forms']
    except:
        pass
    try:
        params['insiders'] = session['insiders']
    except:
        pass
    try:
        params['ciks'] = session['ticker']['cik']
    except:
        pass

    if 'watchlist_view' in session and session['watchlist_view'] == 'true':
        if 'watchlist_ciks' in session:
            params['ciks'] = ','.join([str(x) for x in
                                       session['watchlist_ciks']])
        else:
            params['ciks'] = default_watchlist()

    response = make_api_request('/filings/list/', params)
    pagination = response.get('_pagination_', {'current': None,
                                             'next': None})

    html = generate_filings_template()
    html = html.render(filings=response['_results_'])
    if request.is_xhr:
        return jsonify(html=html, pagination=pagination)
    return render_template('filings.jinja2', html=html,
                           results=response['_results_'],
                           pagination=pagination)


def generate_filings_template():
    html = Template(u'''\
     {% for filing in filings %}
     <tr>
      <td>
        <a style="color:#333;text-decoration:none;"
            href="/filings/{{filing.cik}}">
         {% if filing.ticker %}
           <span style="color:#5586E0;text-decoration:none;">
           {{ filing.ticker }}</span><br>
         {% endif %}
         {{ filing.name | truncator(25)|safe }}
        </a>
      </td>
      <td>{{filing.form}}</td>
      <td>{{filing.date_filed | pretty_date_time }}</td>
      <td>
      <a title="View Original" href="{{ filing.url }}" target="_blank">
        <i class="fa fa-external-link fa-lg"></i>
      </a>
      </td>
    </tr>
    {% endfor %}''')
    return html
