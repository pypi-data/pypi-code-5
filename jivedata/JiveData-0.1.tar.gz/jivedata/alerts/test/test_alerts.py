import unittest
import copy
from ..alerts import Alerts
from jivedata.utils import current_est
from datetime import timedelta

est = current_est().replace(tzinfo=None)
raw_data = [{'accession': '',
             'date_filed': (est - timedelta(minutes=9)).isoformat(),
             'processed': (est - timedelta(seconds=59)).isoformat()
             },
            ]
subscribed_alerts = ['/filings/']
watchlist = [1288776]
funds = [921669]


def raw_to_alert(alert_type, cik):
    new_raw = copy.deepcopy(raw_data)
    new_raw[0]['cik'] = cik
    new_raw[0]['type'] = alert_type
    new_raw[0]['text'] = ''
    new_raw[0]['html'] = ''
    new_raw[0]['subject'] = ''
    return new_raw


class Tester(unittest.TestCase):
    def test_time_filter(self):
        alerts = Alerts('', '')
        test_raw = copy.deepcopy(raw_data)
        self.failUnless(alerts.time_filter(test_raw) == test_raw)

    def test_time_filter_old_date_filed(self):
        alerts = Alerts('', '')
        test_raw = copy.deepcopy(raw_data)
        test_raw[0]['date_filed'] = (est - timedelta(minutes=61)).isoformat()
        self.failUnless(alerts.time_filter(test_raw) == [])

    def test_time_filter_old_processed_time(self):
        alerts = Alerts('', '')
        test_raw = copy.deepcopy(raw_data)
        test_raw[0]['processed'] = (est - timedelta(seconds=61)).isoformat()
        self.failUnless(alerts.time_filter(test_raw) == [])

    def test_in_watchlist(self):
        for alert_type in ['/filings/', '/insiders/']:
            alerts = Alerts('', '')
            alerts.raw_alerts = raw_to_alert(alert_type, watchlist[0])
            alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                    subscribed_alerts=[alert_type])
            self.failUnless(len(alerts.email_alerts) == 1)

            """Test outside of watchlist"""
            alerts.raw_alerts = raw_to_alert(alert_type, cik=90210)
            alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                    subscribed_alerts=[alert_type])
            self.failUnless(alerts.email_alerts == [])

    def test_in_funds(self):
        alert_type = '/13F/'
        alerts = Alerts('', '')
        alerts.raw_alerts = raw_to_alert(alert_type, cik=funds[0])
        alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                subscribed_alerts=[alert_type])
        self.failUnless(len(alerts.email_alerts) == 1)

        """Test outside of funds list"""
        alerts.raw_alerts = raw_to_alert(alert_type, cik=90210)
        alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                subscribed_alerts=[alert_type])
        self.failUnless(alerts.email_alerts == [])

    def test_subscribed_alerts(self):
        subscribed_alerts = ['/filings/', '/insiders/']
        for i, alert_type in enumerate(subscribed_alerts):
            alerts = Alerts('', '')
            alerts.raw_alerts = raw_to_alert(alert_type, watchlist[0])
            alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                    subscribed_alerts=[alert_type])
            self.failUnless(len(alerts.email_alerts) == 1)

        """Test outside of their subscribed alerts"""
        subscribed_alerts = ['/filings/', '/insiders/', '/13F/']
        for i, alert_type in enumerate(subscribed_alerts):
            alerts = Alerts('', '')
            my_alerts = [x for j, x in enumerate(subscribed_alerts)
                         if j != i]
            alerts.raw_alerts = raw_to_alert(alert_type, watchlist[0])
            alerts.watchlist_filter(watchlist=watchlist, funds=funds,
                                    subscribed_alerts=my_alerts)
            self.failUnless(alerts.email_alerts == [])


if __name__ == '__main__':
    unittest.main()
