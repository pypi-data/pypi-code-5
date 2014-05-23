from pysift import errors
import requests
from urlparse import urljoin
import json

SIFTSCIENCE_API_URL = 'https://api.siftscience.com/'
SIFTSCIENCE_API_VERSION = '203'

class SiftScienceCore(object):

    def __init__(self, api_key):
        super(SiftScienceCore, self).__init__()
        self._api_key = api_key
        self._api_url = SIFTSCIENCE_API_URL
        self._api_version = SIFTSCIENCE_API_VERSION
        self._session = requests.session()
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type' : 'application/json'
        })
        self._generate_error_codes()

    def __repr__(self):
        return '<siftscience-core at 0x%x>' % (id(self))

    def _generate_error_codes(self):
        self._error_codes = {
            53: errors.InvalidCharactersInFieldValue,
        }

    def _handle_error(self, status, message):
        exc = self._error_codes.get(status)
        if exc:
            raise exc(status, message)
        else:
            raise errors.SiftError(status, message)


    def _build_url(self, path):
        path = "/v%s%s" % (self._api_version, path)
        return str(urljoin(self._api_url, path))


    def _request(self, method, url, **kwargs):

        data = kwargs.get('data')
        if isinstance(data, dict):
            kwargs['data'] = json.dumps(data)

        try:
            response = self._session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise errors.ServiceError(e.message)

        status = response.json().get('status')
        message = response.json().get('error_message')

        if status != 0:
            self._handle_error(status, message)
        return response.json()


    def track(self, event, properties):
        properties.update({
            "$type": event,
            "$api_key": self._api_key
        })

        return self._request(
            'POST',
            self._build_url('/events'),
            data=properties
        )

    def label(self, user, bad, description, **reasons):
        d = {
            "$api_key": self._api_key,
            "$is_bad": bool(bad),
            "$description": description,
            "$reasons": []
        }

        valid_reasons = [
            '$chargeback',
            '$spam',
            '$funneling',
            '$fake',
            '$referral',
            '$duplicate_account'
        ]

        for reason, value in reasons.items():
            reason = "$%s" % reason
            if reason in valid_reasons:
                d['$reasons'].append(reason)

        return self._request(
            'POST',
            self._build_url('/users/%s/labels' % user),
            data=d
        )

    def score(self, user):
        return self._request(
            'GET',
            self._build_url('/score/%s' % user),
            params={'api_key': self._api_key}
        )




class SiftScience(SiftScienceCore):
    """ Main SiftScience Class """

    def __init__(self, api_key):
        super(SiftScience, self).__init__(api_key)

    def __repr__(self):
        return '<siftscience at 0x%x>' % (id(self))
