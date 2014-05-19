import calendar
from datetime import datetime, timedelta
import hashlib
import json
import urllib
import urllib2

import floraconcierge
from floraconcierge import errors
from floraconcierge.client import handlers
from floraconcierge.client.types import from_dict
from floraconcierge.errors import get_result_error


class Environment(object):
    def __init__(self):
        self.language = 'en'
        self.country = None
        self.city = None
        self.date = ApiClient.get_timestamp()
        self.currency = 'usd'
        self.ip = '127.0.0.1'
        self.promo = None
        self.user_auth_key = None

    @property
    def params(self):
        return {
            '_lang': self.language or '',
            '_country': self.country or '',
            '_city': self.city or '',
            '_date': self.date or '',
            '_currency': self.currency or '',
            '_ip': self.ip,
            '_promo': self.promo or '',
            '_user_auth_key': self.user_auth_key or ''
        }


class ApiResult(object):
    def __init__(self, func, params=None, post=None):
        self.func = func
        self.params = params
        self.post = post
        self.url = None
        self.body = None
        self.http_code = None
        self.time = None

        self.__data = None

    def process(self, response):
        try:
            self.__data = json.loads(response, object_hook=from_dict)
        except ValueError, e:
            self.body = response

            raise errors.MalformedJSONResultError(self, e.message)

        if self.__data.error.code:
            raise get_result_error(self, self.__data.error)

    @property
    def value(self):
        return self.__data.result

    def dump(self):
        return self.value


class ApiClient(object):
    def __init__(self, api_id, secret_key):
        self.__api_id = api_id
        self.__secret_key = secret_key

        self.env = Environment()

        self.__opener = urllib2.build_opener(
            handlers.UserAgentProcessor(floraconcierge.HTTP_CLIENT_UA),
            handlers.GZipProcessor()
        )

        self.__api_endpoint = 'http://api.floraconcierge.com/v1/'
        self.__debug = False
        self.__calls = list()
        self.__calls_time = timedelta()

        # importing here avoid import recursion
        from floraconcierge.services import Manager

        self.services = Manager(self)

    @property
    def api_endpoint(self):
        return self.__api_endpoint

    @api_endpoint.setter
    def api_endpoint(self, url):
        self.__api_endpoint = url

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = bool(value)

    @staticmethod
    def get_timestamp(time=None):
        time = time or datetime.now()

        return calendar.timegm(time.timetuple())

    @property
    def calls(self):
        return self.__calls

    @calls.deleter
    def calls(self):
        self.__calls = list()
        self.__calls_time = timedelta()

    def sign(self, **kwargs):
        sign = dict((k, v) for k, v in kwargs.iteritems() if k[0] != '_')

        keys = sign.keys()
        keys.sort()

        tosign = []
        for k in keys:
            tosign.append("%s=%s" % (k, sign[k]))

        tosign = "".join(tosign)

        return hashlib.sha1("%s:%s" % (self.__secret_key, tosign)).hexdigest()

    def call(self, func, get=None, post=None):
        get, post, start = get or dict(), post or dict(), datetime.now()

        assert isinstance(func, (str, unicode)), 'Supported only string function name'
        assert isinstance(get, dict), 'Supported only dict GET data'
        assert isinstance(post, dict), 'Supported only dict POST data'

        _get, _post = get.copy(), post.copy()

        get.update({
            '_sign': self.sign(**get),
            '_api_id': self.__api_id,
        })
        get.update(self.env.params)

        get = dict((k, v) for k, v in get.iteritems() if k[0] != '_' or v)

        url = "%s%s?%s" % (self.__api_endpoint, func.lstrip(), urllib.urlencode(get))
        request = urllib2.Request(url)
        if _post:
            request.data = json.dumps(_post)

        try:
            response = self.__opener.open(request)
            body = response.read()
        except urllib2.URLError, e:
            raise errors.HTTPError(e, e.reason)

        result = ApiResult(func, _get, _post)
        result.url = response.geturl()
        result.http_code = response.getcode()
        result.time = datetime.now() - start

        if self.debug:
            result.body = body

        self.__calls.append(result)
        self.__calls_time += result.time

        result.process(body)

        return result.value


class Service(object):
    """
    @type client: ApiClient
    """

    def __init__(self, client):
        self.__client = client

    def _callapi(self, func, get=None, post=None):
        return self.__client.call(func, get, post)
