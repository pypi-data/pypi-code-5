import urllib
import urllib2
import greader.utils


class API:
    def __init__(self, username, password):
        self._api_base = 'http://www.google.com/reader/api/0/'
        self._headers = {}

        (self._username, self._password) = (username, password)
        self._is_auth = False

    def login(self):
        url = 'https://www.google.com/accounts/ClientLogin'
        params = urllib.urlencode({
            'Email': self._username,
            'Passwd': self._password,
            'service': 'reader'
            })
        req = urllib2.Request(url, data=params)
        resp = urllib2.urlopen(req)
        content = resp.read()
        d = dict(x.split('=') for x in content.split('\n') if x)

        self._headers['Cookie'] = content.replace('\n', '; ')
        self._headers['Authorization'] = 'GoogleLogin auth=%s' % (d["Auth"])
        self._is_auth = True

    def _get_token(self):
        if not self._is_auth:
            return None

        url = self._api_base + "token"
        req = urllib2.Request(url, None, self._headers)
        resp = urllib2.urlopen(req)
        content = resp.read()
        return content

    def _run_req(self, url, params={}):
        url = self._api_base + url
        data = urllib.urlencode(params)
        req = urllib2.Request(url, data, self._headers)
        return urllib2.urlopen(req)

    """
    params need keys: title, action, stream
    """
    def edit_feed(self, params):
        url = self._api_base + "subscription/edit?client=contact:mname-at-gmail"
        params['T'] = self._get_token()

        if 'action' in params:  # (subscribe, unsubscribe)
            params['ac'] = params['action']
            del(params['action'])

        if 'title' in params:
            params['t'] = params['title']
            del(params['title'])

        if 'stream' in params:
            params['s'] = params['stream']
            del(params['stream'])

        self._run_req(url, params).read()

    """
    Adds a tag to item
    """
    def add_tag(self, tag, stream, item):
        params = {
            'a': 'user/-/state/com.google/' + tag,  # a/r insert remove
            'async': 'true',
            'i': item,
            's': stream,
            'pos': 1,
            'T': self._get_token()
            }
        self._run_req("edit-tag?client=foobar", params).read()

    def remove_tag(self, tag, stream, item):
        params = {
            'r': 'user/-/state/com.google/' + tag,  # a/r insert remove
            'async': 'true',
            'i': item,
            's': stream,
            'pos': 1,
            'T': self._get_token()
            }
        self._run_req("edit-tag?client=foobar", params).read()

    """
    Return a list of tagged items. Possible tags are 'broadcast', 'like' and 'starred'
    """
    def list_tag(self, tag, continuation=None):
        url = 'http://www.google.com/reader/atom/user/-/state/com.google/'+tag+'?n=300&c='

        if continuation is not None:
            url = url + continuation

        buffer = self.fetch_raw_url(url)
        ret = greader.utils.get_items_from_string(buffer)

        continuation = greader.utils.get_continuation_from_string(buffer)
        if continuation:
            print "Continuation: ", continuation
            ret = ret + self.list_tag(tag, continuation)

        return ret

    """
    Fetch URL as-is using credentials
    """
    def fetch_raw_url(self, url):
        return urllib2.urlopen(urllib2.Request(url, None, self._headers)).read()
