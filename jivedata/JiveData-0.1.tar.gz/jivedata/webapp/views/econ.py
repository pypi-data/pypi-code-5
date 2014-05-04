from flask import (request, session, jsonify, render_template,
                   flash, redirect, url_for)
from jinja2 import Template
from jivedata.webapp import app
from jivedata.webapp.views.utils import make_api_request


@app.route('/econ/search/')
def econ_search():
    """Econ Autocomplete"""
    params = {'term': request.args.get('term'), 'number': 10}
    response = make_api_request('/econ/search/', params, True)
    return jsonify(results=response['_results_'])


@app.route('/econ/')
def econ_list():
    """Get a list of most recent economic updates"""
    if 'series' in session and session['series'] != '':
        return(redirect('/econ/' + str(session['series']['id'])))
    params = {}
    try:
        page = int(request.args.get('page'))
    except:
        page = None
    if page != None:
        params['page'] = page

    if 'most_viewed' in session and session['most_viewed'] == 'true':
        params['popularity'] = 50

    response = make_api_request('/econ/list/', params)
    pagination = response.get('_pagination_', {'current': None,
                                             'next': None})

    html = generate_econ_template()
    html = html.render(series=response['_results_'])
    if request.is_xhr:
        return jsonify(html=html, pagination=pagination)

    flash("Don't worry, we're gonna bring back the charts shortly", 'info')
    return render_template('econ.jinja2', html=html, pagination=pagination)


def generate_econ_template():
    h = Template(u'''
    {% for s in series %}
    <tr>
      <td>
          <a style="color:#333;text-decoration:none;"
          href="/econ/{{ s.id }}"><small>{{ s.id }}</small><br>
          {{ s.name|safe }}</a><br>
          <small>
          ({{ s.units }},
          {{ s.frequency | frequency_long }}, {{ s.seasonal }})
          </small>
      </td>
      <td>{{ s.updated | pretty_date_time }}</td>
      <td><strong>{{ s.latest_date | safe }}: </strong>{{ s.latest }}
        <br>{{ s.sequential_change }} <small>vs. </small>
        {{ s.frequency | prior_wording }} <small>({{ s.prior }})</small>
        <br>{{ s.yoy_change }} <small>vs. </small>
        Yr Ago <small>({{ s.year_ago }})</small></td>
      <td>
        <a title="View Chart" style="cursor:pointer;" href="/econ/{{ s.id }}">
        <i class="fa fa-bar-chart-o fa-lg" style="cursor:pointer;"></i></a>
      </td>
    </tr>
    {% endfor %}
    ''')
    return h


@app.route('/econ/<series>/')
def econ_detail(series):
    """Get the history of an economic series."""
    params = {'reverse': 'true', 'length': -100}
    series = series.upper()

    if app.config['test_data'] == True:
        if series != 'GDP':
            return redirect('/econ/GDP/')

    params['series'] = series
    response = make_api_request('/econ/detail/', params)

    if '_error_' in response:
        flash(response['_error_'], 'danger')
        return redirect(url_for('econ_list'))
    else:
        session['series'] = {'id': series,
                             'name': response['_results_'][series]['name']}

        flash("Don't worry, we're gonna bring back the charts shortly", 'info')
        return render_template('econ.jinja2', series=series,
                               results=response['_results_'])
