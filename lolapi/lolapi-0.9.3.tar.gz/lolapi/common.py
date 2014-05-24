import requests
import urlparse

from exceptions import UnsupportedRegion

class Resource(object):

    def __init__(self, api):
        self.api = api
        self.scheme = u'https'
        self.netloc = u'prod.api.pvp.net'
        self.query = u'api_key=%s' % api.key

    def _check_region(self):
    	if not (self.api and self.api.region in self.available_regions):
            raise UnsupportedRegion()

    def _construct_url(self, path):
        """
        Builds the request url.
        urlparse expects 6 tuple:
        (scheme, netloc, path, params, query, fragment)
        """
        args = (self.scheme, self.netloc, path, '', self.query, '')
        return unicode(urlparse.urlunparse(args))

    def get(self, path):
        self._check_region()
        url = self._construct_url(path)
        r = requests.get(url, verify=True)
        r.raise_for_status()
        return r.json()