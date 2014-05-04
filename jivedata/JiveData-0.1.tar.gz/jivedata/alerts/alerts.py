"""A handler for email and twitter notifications"""
from datetime import timedelta
import dateutil
from jivedata.utils import (Client, truncator, format_value, format_aum,
                    date_time_to_string, pretty_date, current_est,
                    string_to_eastern_datetime, format_number,
                    insider_position, prior_wording)


class Alerts(Client):
    """Retrieve alerts from the API, prepare and send both
    email alerts and tweets"""
    def __init__(self, client_id, client_secret,
                 endpoints=[], params={}):

        self.nyc_datetime = current_est().replace(tzinfo=None)
        super(Alerts, self).__init__(client_id=client_id,
                                    client_secret=client_secret)
        self.endpoints = endpoints
        self.params = params
        for endpoint in self.endpoints:
            if endpoint not in self.params:
                self.params[endpoint] = {}
        self.params = params
        self.filings, self.insiders, self.institutional, self.econ = \
                                                ([] for i in range(4))

        self.raw_alerts = []
        self.get_resources()

    def get_resources(self):
        """Get the new data from the API"""
        if '/filings/' in self.endpoints:
            self.get_protected(endpoint='/filings/new/',
                               params=self.params['/filings/'])
            self.filings = self.time_filter(self.results['_results_'])
            for filing in self.filings:
                self.format_sec(filing)

        if '/insiders/' in self.endpoints:
            self.get_protected(endpoint='/insiders/new/',
                               params=self.params['/insiders/'])
            self.insiders = self.time_filter(self.results['_results_'])
            for filing in self.insiders:
                self.format_insiders(filing)

        if '/13F/' in self.endpoints:
            self.get_protected(endpoint='/13F/new/',
                               params=self.params['/13F/'])
            self.institutional = self.time_filter(self.results['_results_'])
            for filing in self.institutional:
                self.format_institutional(filing)

        if '/econ/' in self.endpoints:
            self.get_protected(endpoint='/econ/new/',
                               params=self.params['/econ/'])
            self.econ = self.time_filter(self.results['_results_'])
            for series in self.econ:
                self.format_econ(series)

    def time_filter(self, raw):
        """The API will always return the latest filings. This will
        filter the filings via time"""
        new = []
        for x in raw:
            if 'date_filed' in x:
                df = dateutil.parser.parse(x['date_filed'])
            elif 'updated' in x:
                df = dateutil.parser.parse(x['updated'])
            processed = dateutil.parser.parse(x['processed'])
            if df > (self.nyc_datetime - timedelta(minutes=60)):
                if processed > (self.nyc_datetime - timedelta(seconds=60)):
                    new.append(x)
        return new

    def format_date_filed(self, d):
        """Convert string date to Apr 7, 2014 2:51PM (EST)"""
        est = string_to_eastern_datetime(d)
        return 'Filed: ' + date_time_to_string(est) + ' (EST)'

    def add_html(self, base_url='www.jivedata.com/',
                 unsubscribe_url='https://api.jivedata.com/me/',):
        """Create the html from the text portion and add the urls"""
        def create_link(text, url, decoration='none', color='#5586e0'):
            return ('<a style="color:' + color + ';text-decoration:' +
                    decoration + ';" ' + 'href="' + url + '">' + text + '</a>')

        def create_span(inner='', font_size='12px', color='#444444',
                        family='Arial,Helvetica,sans-serif'):
            return ('<span style="color:' + color + ';font-size:' +
                    font_size + ';font-family:' + family + ';">' +
                    inner + '</span>')

        self.twitter = []
        for alert in self.raw_alerts:
            """Create the html from the text"""
            alert['html'] = []
            for i, line in enumerate(alert['text']):
                span = create_span(inner=line)
                if i == 0:
                    span = create_span(inner=line, font_size='14px',
                                       color='#000000')
                alert['html'].append(span)

            """Add the links"""
            url = base_url + alert['type']
            if 'ticker' in alert and alert['ticker'] != None:
                url += alert['ticker'] + '/'
            elif 'cik' in alert:
                url += str(alert['cik']) + '/'
            elif 'id' in alert:
                url += str(alert['id']) + '/'

            if 'tweet' in alert:
                alert['tweet'].append(url)

            unsubscribe_text = 'To manage your alert settings'
            """Create text links"""
            alert['text'].append(url)
            alert['text'].append('')
            if 'original' in alert:
                alert['text'].append('View Original: ' + alert['original'])
            alert['text'].append(unsubscribe_text + ': ' + unsubscribe_url)

            """Create html links"""
            link = create_link(url, url)
            span = create_span(inner=link, color='#5586e0;')
            alert['html'].append(span)

            alert['html'].append('')
            if 'original' in alert:
                link = create_link('View original', alert['original'])
                span = create_span(inner=link, font_size='11px')
                alert['html'].append(span)

            link = create_link('click here', unsubscribe_url, color='#444444')
            span = create_span(inner=link, font_size='11px')
            span = create_span(inner=unsubscribe_text + ' ' + span,
                               font_size='11px', color='#666666')
            alert['html'].append(span)

    def format_sec(self, filing):
        alert = {'type': '/filings/', 'cik': int(filing['cik']),
                 'original': filing['url']}
        date_filed = self.format_date_filed(filing['date_filed'])
        alert['subject'] = '%s filed a form %s' % \
                            (filing['name'], filing['form'])
        alert['text'] = [alert['subject']]
        alert['text'].append(date_filed)

        alert['ticker'] = filing['ticker']

        """Tweets for sec filings are handled by financials"""
        self.raw_alerts.append(alert)

    def format_econ(self, series):
        alert = {'type': '/econ/', 'id': series['id']}
        title = truncator(series['name'], 25)
        units = truncator(series['units_short'], 15)

        alert['subject'] = '%s (%s, %s) ' % (title, units, series['seasonal'])
        alert['subject'] += pretty_date(series['latest_date']) + ': '
        alert['subject'] += series['latest'] + ', '
        alert['subject'] += series['sequential_change'] + ' vs. '
        alert['subject'] += prior_wording(series['frequency']) + ' and '
        alert['subject'] += series['yoy_change'] + ' YoY'

        """Create the text body"""
        """Will implement when we get econ watchlists setup"""
        alert['text'] = [alert['subject']]

        """Create the tweet"""
        if series['popularity'] > 50:
            alert['tweet'] = [alert['subject']]
        self.raw_alerts.append(alert)

    def format_insiders(self, filing):
        alert = {'type': '/insiders/', 'cik': int(filing['cik']),
                 'original': filing['url']}
        date_filed = self.format_date_filed(filing['date_filed'])
        insider = truncator(filing['insider_name'], 40)
        company = truncator(filing['name'], 40)
        net_value = filing['option_value'] - filing['value']
        bought_sold = 'sold a net'
        if filing['shares'] > 0:
            bought_sold = 'bought a net'

        alert['subject'] = '%s %s %s in %s' % (insider, bought_sold, \
                            format_value(abs(net_value)), company)
        """Create the text body"""
        alert['text'] = [alert['subject']]
        alert['text'].append(insider_position(filing))
        alert['text'].append(date_filed)
        alert['ticker'] = filing['ticker']

        """Create the tweet"""
        if filing['ticker'] != None:
            tweet = '$' + filing['ticker'] + ': '
            alert['tweet'] = [tweet + alert['subject']]
        self.raw_alerts.append(alert)

    def format_institutional(self, filing):
        alert = {'type': '/13F/', 'cik': int(filing['cik']),
                 'original': filing['url']}
        company = truncator(filing['name'], 40)

        if filing['amendment'] == 'A':
            amended_wording = 'an amended 13F'
        elif filing['amendment'] == 'R':
            amended_wording = 'a replacement 13F'
        else:
            amended_wording = 'a 13F'

        date_filed = self.format_date_filed(filing['date_filed'])
        period_of_report = pretty_date(filing['period_of_report'])
        positions = format_number(filing['positions'])
        aum = format_aum(filing['aum'])
        alert['subject'] = '%s filed %s for %s' % \
                    (company, amended_wording, period_of_report)

        """Create the text body"""
        alert['text'] = [alert['subject']]
        alert['text'].append(date_filed)
        alert['text'].append('Period: ' + period_of_report)
        alert['text'].append('Positions: ' + positions + ' (%s)' % aum)

        """Create the tweet"""
        alert['tweet'] = [alert['subject']]
        alert['tweet'].append(positions + ' positions ' + '(' + aum + ')')
        self.raw_alerts.append(alert)

    def create_twitter_alerts(self):
        """Twitter alerts. SEC alerts are handled by
        financials, which will be implemented shortly"""
        self.twitter_alerts = [{'type': x['type'], 'tweet': x['tweet']}
                               for x in self.raw_alerts if 'tweet' in x and
                               x['type'] in ['/insiders/', '/13F/', '/econ/']]

        for alert in self.twitter_alerts:
            alert['tweet'] = '. '.join(alert['tweet'])

    def watchlist_filter(self, watchlist=[],
                            funds=[], subscribed_alerts=[]):
        """Make sure the user is subscribed to that alert and that the
        cik is either in their watchlist or funds list"""
        self.email_alerts = []

        for alert in self.raw_alerts:
            if alert['type'] in subscribed_alerts:
                email_alert = {'text': alert['text'], 'html': alert['html'],
                              'subject': alert['subject']}

                if alert['type'] in ['/insiders/', '/filings/'] and \
                            alert['cik'] in watchlist:
                        self.email_alerts.append(email_alert)

                elif alert['type'] == '/13F/' and alert['cik'] in funds:
                        self.email_alerts.append(email_alert)

        for alert in self.email_alerts:
            alert['text'] = '\r\n'.join(alert['text'])
            alert['html'] = '<br>'.join(alert['html'])
