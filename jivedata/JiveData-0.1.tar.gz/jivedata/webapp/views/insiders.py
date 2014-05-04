from flask import (request, jsonify, render_template,
                   flash, session, redirect)
from jinja2 import Template
from jivedata.webapp import app
from jivedata.webapp.views.utils import (make_api_request, store_cik,
                                         default_watchlist)


@app.route('/insiders/', defaults={'cik': None})
@app.route('/insiders/<cik>/')
def insiders(cik):
    """Get the latest insider filings. If cik is not None then get the
    latest insider filings for a specific company"""
    if cik is None and 'ticker' in session and session['ticker'] != {}:
        cik = session['ticker']['cik']

    if cik is not None:
        store_cik(cik)
        if session['ticker'] == {}:
            flash('Invalid ticker', 'danger')
            return redirect('/insiders/')

    params = {}
    if 'planned' in session:
        params['planned'] = session['planned']

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

    try:
        page = int(request.args.get('page'))
    except:
        page = None
    if page != None:
        params['page'] = page

    response = make_api_request('/insiders/list/', params)
    pagination = response.get('_pagination_', {'current': None,
                                             'next': None})

    tmplate = generate_insider_template()
    html = tmplate.render(insiders=response['_results_'], session=session)
    if request.is_xhr:
        return jsonify(html=html, pagination=pagination)
    flash("Don't worry, we're gonna bring back the charts shortly", 'info')
    return render_template('insiders.jinja2', html=html, pagination=pagination)


def generate_insider_template():
    h = Template(u'''\
    {% for insider in insiders %}
    {%- set color='green' -%}{% set bought_sold = 'Purchased' -%}
    {% if insider.shares < 0 -%}
      {% set color='red' %}{% set bought_sold = 'Sold' -%}
    {%- endif %}
    <tr>
      <td>
        <small>Date Filed: {{ insider.date_filed | pretty_date_time }}</small>
        <br>
        {% if not session['ticker'] or session['ticker'] == {} -%}
          <a style="color:#333;text-decoration:none;"
             href="/insiders/{{ insider.cik }}">
            {% if insider.ticker != null %}
              <span style="color:#5586E0;">{{ insider.ticker }}</span>
            {% endif %}
            {{ insider.name | truncator(40) | safe }}
          </a><br>
        {%- endif %}
        {{ insider.insider_name | truncator(20) | safe }}
        <span style="color:#666;">
          <small>{{ insider | insider_position }}</small>
        </span>
      </td>
      <td>
        <small>
          Transaction Date: {{ insider.period_of_report | pretty_date }}
        </small><br>
        {% if insider.option_shares != 0.00 -%}
          Exercised
          <span style="color:green;">
            {{ insider.option_shares | format_value }}
          </span> options
          <small>
            ({{ insider.option_shares | format_shares }} options @
            {{ insider.option_value | avg_price(insider.option_shares) }})
          </small><br>
        {%- endif %}
        {{ bought_sold }}
        <span style="color:{{ color }};">
          {{ insider.value | format_value }}
        </span>
        <small>
          ({{ insider.shares | format_shares }} shares @
          {{ insider.value | avg_price(insider.shares) }})
        </small>
        {% if insider.option_shares != 0.00 -%}
          {% set net_proceeds = insider.option_value - insider.value %}
          {% set net_shares = insider.option_shares + insider.shares %}

          {% if net_proceeds < 0 -%}
            <br>Net Proceeds of
              <span style="color:red;">
                {{ net_proceeds|abs|format_value }}
              </span>
          {% else %}
            <br>Net Cost of <span style="color:green;">
            {{ net_proceeds|abs|format_value }}</span>
          {%- endif %}

          {% if net_shares >= 0 -%}
            <small>(+{{ net_shares|format_shares }} shares)</small>
          {% else %}
            <small>(-{{ net_shares|format_shares}} shares)</small>
          {%- endif %}
        {%- endif %}
      </td>
      <td>
        {% if not session['ticker'] or session['ticker'] == {} %}
          <a title="View Insider Filings" href="/insiders/{{ insider.cik }}">
            <i class="fa fa-bar-chart-o fa-lg"></i>
          </a>
        {% endif %}
        <a title="View Original" href="{{ insider.url }}" target="_blank">
          <i class="fa fa-external-link fa-lg"></i>
        </a>
      </td>
    </tr>
    {% endfor %}
    ''')
    return h
