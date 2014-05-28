#!/usr/bin/env python3

__all__ = ['std','client','common','details','FileDownloader','HTTPDownloader']

#USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0"
#USER_AGENT = "Mget/0.6.4 (Linux; Mac OS X; en-us)"

import os
import sys
import urllib.request as urllib
import urllib.parse as urlparse
import http.cookiejar as cookiejar

from .common import FileDownloader
from .http import HTTPDownloader

class Default(object): pass

std = Default()
std.UA = "Mget/0.6.4 (Linux; Mac OS X; en-us)"
std.FUA = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0"

