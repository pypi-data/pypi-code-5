# -*- coding: utf-8 -*-

# ConstantDict as detailed at
# http://loose-bits.com/2011/06/constantdict-yet-another-python.html


class ConstantDict(object):
    """An enumeration class."""
    _dict = None

    @classmethod
    def dict(cls):
        """Dictionary of all upper-case constants."""
        if cls._dict is None:
            val = lambda x: getattr(cls, x)
            cls._dict = dict(((c, val(c)) for c in dir(cls)
                             if c == c.upper()))
        return cls._dict

    def __contains__(self, value):
        return value in self.dict().values()

    def __iter__(self):
        for value in self.dict().values():
            yield value

    def __getattr__(self, name):
        if name in self.dict():
            return self._dict[name]
        else:
            return object.__getattribute__(self, name)


class MsgFields(ConstantDict):
    ASNIP = "asnip"
    ARTIFACT = "arte"
    DOMAIN = "dom"
    GEOIP = "geoip"
    HOSTNAME = "host"
    HTTP_STATUS = "httpstat"
    IP = "ip"
    PATH = "path"
    SCREENSHOT = "sshot"
    SPIDER = "spider"
    URL = "url"
    WHOIS = "whois"
    WHOIS_RAW = "raw"

    META = "_"
    META_START_TIME = "stime"
    META_END_TIME = "etime"
    META_SUCCESS = "ok"
    META_RESULT = "r"
    META_VERSION = "v"
    META_ERR = "e"
    META_MSG = "m"
