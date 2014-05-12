import requests
from . import lookup
from . import shorten

class UnauthorizedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class api:
    def __init__(self, apikey = "APIKEYHERE"):
        self.apikey = apikey
    def lookup(self, url):
        return lookup.lookup(self.apikey, url)
    def shorten(self, url, temp = False):
        return shorten.shorten(self.apikey, url, temp)

