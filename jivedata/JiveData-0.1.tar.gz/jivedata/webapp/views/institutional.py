from flask import (request, session, jsonify, render_template,
                   redirect, flash, url_for)
from datetime import datetime
from jinja2 import Template
from jivedata.webapp import app
from jivedata.webapp.views.utils import make_api_request, default_funds
from jivedata.utils import format_aum


@app.route('/13f/search/')
@app.route('/13F/search/')
def institutional_search():
    """13F Autocomplete"""
    params = {'term': request.args.get('term'), 'number': 10}
    response = make_api_request('/13F/search/', params, True)
    for f in response['_results_']:
        f['aum'] = format_aum(f['aum'])
        latest_filing = datetime.strptime(f['latest_filing'], '%Y-%m-%d')
        latest_filing = datetime.strftime(latest_filing, '%m/%d/%Y')
        if latest_filing.startswith('0'):
            latest_filing = latest_filing.replace('0', '', 1)
        f['latest_filing'] = latest_filing
    return jsonify(results=response['_results_'])


@app.route('/13f/')
@app.route('/13F/')
def institutional_list():
    """13F list view"""
    if 'fund' in session and session['fund'] != '':
        return(redirect('/13F/' + str(session['fund']['cik'])))

    params = {}
    try:
        page = int(request.args.get('page'))
    except:
        page = None
    if page != None:
        params['page'] = page

    if 'my_funds_view' in session and session['my_funds_view'] == 'true':
        if 'funds_ciks' in session:
            params['ciks'] = ','.join([str(x) for x in
                                       session['funds_ciks']])
        else:
            params['ciks'] = default_funds()

    response = make_api_request('/13F/list/', params)
    pagination = response.get('_pagination_', {'current': None,
                                             'next': None})
    tmplate = generate_institutional_template()
    html = tmplate.render(institutional=response['_results_'])

    if request.is_xhr:
        return jsonify(html=html, pagination=pagination)
    return render_template('institutional.jinja2', html=html,
                           results=response['_results_'],
                           pagination=pagination)


def generate_institutional_template():
    html = Template(u'''
    {% for inst in institutional %}
        <tr onclick="">
        <td>
            <a style="color:#333;text-decoration:none;"
              href="/13F/{{ inst.cik }}">{{ inst.name }}
            {% if inst.amendment == 'R' -%}
              <br>
              <span style="color:red;">
                <small>Replacement</small>
              </span>
            {% endif %}
           {% if inst.amendment in ['O','R'] -%}
            <br>
            <small>
               Reported AUM: {{ inst.aum | format_aum }}
               ({{ inst.positions | format_number }} positions)
            </small>
            </a>
           {% endif %}
           {% if inst.amendment == 'A' -%}
            <br>
            <span style="color:red;">
               <small>Amendment</small></span>
               <br><small>Additions: {{ inst.aum | format_aum }}
               ({{ inst.positions | format_number }} positions)
               </small>
            </a>
           {% endif %}
        </td>
        <td>
          {{ inst.period_of_report | pretty_date }}
        </td>
        <td>
          {{ inst.date_filed | pretty_date_time }}
        </td>
        <td>
          <a href="/13F/{{ inst.cik }}">
            <i class="fa fa-folder-open-o fa-lg"></i>
          </a>
        </td>
      </tr>
     {% endfor %}''')
    return html


@app.route('/13f/<int:cik>/')
@app.route('/13F/<int:cik>/')
def institutional_detail(cik):
    """Compare 2 periods for a 13F filer"""
    if app.config['test_data'] == True:
        if cik != 1079114:
            return redirect('/13F/1079114/')
    params = {'cik': cik, 'length': -2}
    response = make_api_request('/13F/detail/', params)

    periods = sorted([datetime.strptime(x, '%Y-%m-%d') for x
                      in response['_results_'].keys()])
    periods = [datetime.strftime(x, '%Y-%m-%d') for x in periods]

    master = []
    current, prior = {}, {}

    if response['_results_'] == {}:
        flash('Invalid fund', 'danger')
        return redirect(url_for('institutional_list'))

    for item in response['_results_'][periods[-1]]['_holdings_']:
        current[item['cusip']] = item
    for item in response['_results_'][periods[0]]['_holdings_']:
        prior[item['cusip']] = item

    total_value = 0
    previous_total_value = 0
    for cusip, v in current.iteritems():
        total_value += int(v['value'])
        tmp = v.copy()
        tmp['prior_shares'] = 0
        tmp['prior_value'] = 0
        tmp['action'] = 'New'
        if cusip in prior:
            tmp['prior_shares'] = prior[cusip]['shares']
            tmp['prior_value'] = prior[cusip]['value']
            if v['shares'] > tmp['prior_shares']:
                tmp['action'] = 'Increased'
            elif v['shares'] < tmp['prior_shares']:
                tmp['action'] = 'Decreased'
            elif v['shares'] == tmp['prior_shares']:
                tmp['action'] = 'No Change'
        master.append(tmp)
    for cusip, v in prior.iteritems():
        previous_total_value += int(v['value'])
        if cusip not in current:
            tmp = v.copy()
            tmp['shares'] = 0
            tmp['value'] = 0
            tmp['prior_shares'] = v['shares']
            tmp['prior_value'] = v['value']
            tmp['action'] = 'Sold All'
            master.append(tmp)

    master = sorted(master, key=lambda k: k['name'])
    for item in master:
        item['share_change'] = item['shares'] - item['prior_shares']
        try:
            item['share_change_percent'] = float(float(item['shares']) /
                                                 float(item['prior_shares'])
                                                 ) - 1
        except ZeroDivisionError:
            item['share_change_percent'] = 1
        item['value_change'] = item['value'] - item['prior_value']
        try:
            item['value_change_percent'] = float(float(item['value']) /
                                                 float(item['prior_value'])
                                                 ) - 1
        except ZeroDivisionError:
            item['value_change_percent'] = 1
        try:
            item['percent'] = float(float(item['value']) / float(total_value))
        except:
            item['percent'] = 0
        try:
            item['prior_percent'] = float(float(item['prior_value']) /
                                          float(previous_total_value))
        except:
            item['prior_percent'] = 0

    try:
        total_value_change = float(total_value) - float(previous_total_value)
    except:
        total_value_change = 0
    try:
        total_value_change_percentage = float(float(total_value) /
                                              float(previous_total_value)) - 1
    except:
        total_value_change_percentage = 0

    tmplate = institutional_detail_template()
    html = tmplate.render(institutional=response['_results_'],
                  periods=periods, master=master,
                  total_value=total_value,
                  previous_total_value=previous_total_value,
                  total_value_change=total_value_change,
                  total_value_change_percentage=total_value_change_percentage)

    session['fund'] = {'cik': cik, 'name':
                response['_results_'][periods[-1]]['_cover_']['manager']}

    return render_template('institutional.jinja2', html=html, detail='true')


def institutional_detail_template():
    html = Template(u'''\
    {% set most_recent = institutional[periods[-1]] -%}
    {% if periods | length == 2 -%}
      {% set prior = institutional[periods[-1]] %}
    {%- endif %}
    {% set cover = most_recent['_cover_'] -%}
    {% set signature = most_recent['_signature_'] -%}
    {% set summary = most_recent['_summary_'] -%}
    <div class="row-fluid">
      <div class="span12 well well-small" style="background-color:#fff;">
        <div class="span5">
          {% if 'manager' in cover -%}
            <div><strong>{{ cover['manager'] }}</strong></div>
          {%- endif %}
          {% if 'street1' in cover %}
            <div>{{ cover['street1'] }}</div>
          {%- endif -%}
          {% if 'street2' in cover -%}
            <div>{{ cover['street2'] }}</div>
          {%- endif -%}
          {% if 'city' in cover or 'state' in cover or 'zip' in cover -%}
          <div>
            {% if 'city' in cover %}{{ cover['city'] }}, {% endif %}
            {% if 'state' in cover %}{{ cover['state'] }} {% endif %}
            {% if 'zip' in cover %}{{ cover['zip'] }}{% endif %}
          </div>
          {%- endif -%}
        </div>
        <div class="span4">
          <div>
            <strong>{{ signature['name'] }}</strong>
          </div>
          <div>
            {{ signature['title'] }}
          </div>
          <div>
            {{ signature['phone'] }}
          </div>
          <div>
            {{ signature['city'] }}, {{ signature['state'] }}
          </div>
        </div>
        <div class="span3">
          <div>
            <strong>Most Recent:</strong>
            &nbsp;{{ periods[-1] | pretty_date }}
          </div>
          {%- if periods | length > 1 -%}
            <div>
              <strong>Prior Period:</strong>
              &nbsp;{{ periods[0] | pretty_date }}
            </div>
          {%- endif -%}
        </div>
      </div>
    </div>

    <table id="datagrid_detail" class="table table-hover">
      <thead>
        <tr>
          <th style="text-align:left;">Company</th>
          <th style="text-align:right;">
            Shares<br><small>(Previous)</small>
          </th>
          <th style="text-align:right;">Shares &plusmn;</th>
          <th style="text-align:right;">
            Mkt Value (x1000)<br><small>(Previous)</small>
          </th>
          <th style="text-align:right;">
            Mkt Value (x1000) &plusmn;
          </th>
          <th style="text-align:right;">% of Total (Mkt Value)<br>
            <small>(Previous)</small>
          </th>
        </tr>
      </thead>
      <tbody>
      {% for item in master %}
      <tr>
        <td style="text-align:left;">
          {% if 'putcall' in item -%}
            <small>{{ item['putcall'] }}</small><br>
          {%- endif %}
          {% if 'type' in item and item['type'] == 'PRN' -%}
            <small>Bond</small><br>
          {%- endif %}
          {% if 'class' in item and item['class'] | upper != 'COM' -%}
            <small>{{ item['class'] }}</small><br>
          {%- endif %}
          {% if 'type' in item and item['type'] == 'SH' and
              'ticker' in item and item['ticker'] != '' -%}
            <span style="color:#5586E0">
              <small>{{ item['ticker'] }}</small>
            </span><br>
          {%- endif %}
          {{ item['name'] }}
        </td>
        <td style="text-align:right;">
          {{ item['shares'] | format_number }}<br>
          <small>{{ item['prior_shares'] | format_number }}</small>
        </td>
        {% if item['action'] in ['New', 'Increased'] -%}
          <td style="color:green;text-align:right;">{{ item['action'] }}
            {% if item['action'] == 'Increased' -%}
            <br><small>+{{ item['share_change'] | format_number }}
            ({{ item['share_change_percent'] | format_percentage}})</small>
            {%- endif %}
          </td>
        {% elif item['action'] in ['Sold All','Decreased'] %}
          <td style="color:red;text-align:right;">{{ item['action'] }}
          {% if item['action'] == 'Decreased' -%}
            <br>
            <span>
              <small>{{ item['share_change'] | format_number }}
              ({{ item['share_change_percent'] | format_percentage}})
              </small>
            </span>
          </td>
          {% endif %}
        {% else %}
        <td style="text-align:right;">{{ item['action'] }}</td>
        {% endif %}
        <td style="text-align:right;">{{ item['value'] | format_currency }}
          {% if 'putcall' in item -%}
            <small>({{ (100*item['value']) | per_share(item['shares']) | format_per_share_currency }}/option)</small>
          {% elif 'type' in item and item['type'] == 'PRN' -%}
            <small>({{ (item['value'] * 1000) | per_share(item['shares']) | format_percentage }} of FV)</small>
          {%- else -%}
            <small>({{ (item['value'] * 1000) | per_share(item['shares']) | format_per_share_currency }}/share)</small>
          {%- endif %}
          <br>
          <small>{{ item['prior_value'] | format_currency }}
          {% if 'putcall' in item -%}
            ({{ (100*item['prior_value']) | per_share(item['prior_shares']) | format_per_share_currency }}/option)
          {% elif 'type' in item and item['type'] == 'PRN' -%}
            ({{ (item['prior_value'] * 1000) | per_share(item['prior_shares']) | format_percentage }} of FV)
          {% else -%}
            ({{ (item['prior_value'] * 1000) | per_share(item['prior_shares']) | format_per_share_currency }}/share)<br>
          {%- endif %}
          </small>
        </td>

        {% if item['value_change'] > 0 -%}
        <td style="color:green;text-align:right;">
          +{{ item['value_change'] | format_currency}} <small>({{ item['value_change_percent'] | format_percentage }})</small>
        </td>
        {% elif item['value_change'] < 0 -%}
        <td style="color:red;text-align:right;">
          {{ item['value_change'] | format_currency}} <small>({{ item['value_change_percent'] | format_percentage }})</small>
        </td>
        {% else -%}
        <td style="text-align:right;">
          {{ item['value_change'] | format_currency}}
        </td>
        {%- endif %}
        <td style="text-align:right;">
          {{ item['percent'] | format_percentage }}<br>
          <small>{{ item['prior_percent'] | format_percentage }}</small>
        </td>
      </tr>
      {%- endfor %}
      <tr>
        <td style="text-align:left;">
          <strong>Total</strong>
        </td>
        <td style="text-align:right;">
          <strong>--<br><small>--</small></strong>
        </td>
        <td style="text-align:right;">
          <strong>--<br><small>--</small></strong>
        </td>
        <td style="text-align:right;">
          <strong>{{ total_value | format_currency }}<br>
          <small>{{ previous_total_value | format_currency }}</small>
          </strong>
        </td>
        {% if total_value_change > 0 -%}
          <td style="color:green;text-align:right;">
            <strong>+{{ total_value_change | format_currency }} <small>({{ total_value_change_percentage | format_percentage }})</small></strong>
          </td>
        {% elif total_value_change < 0 -%}
          <td style="color:red;text-align:right;">
            <strong>{{ total_value_change | format_currency }} <small>({{ total_value_change_percentage | format_percentage }})</small></strong>
          </td>
        {% else -%}
          <td style="text-align:right;">
            <strong>--</strong>
          </td>
        {%- endif %}
          <td style="text-align:right;">
            <strong>100%<br><small>100%</small></strong>
          </td>
      </tr>
      </tbody>
    </table>
    ''')
    return html
