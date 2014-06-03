#!/usr/bin/env python3

__all__ = ['std','client','common','details', 'ExtractorError', 'DownloadError']

import os
import sys
import urllib.request as urllib
import urllib.parse as urlparse
import http.cookiejar as cookiejar
from .exception import ExtractorError, DownloadError

def write_string(s, out = None):
	if out is None: out = sys.stderr
	assert type(s) == str

	out.write(s+"\n")
	out.flush()

report = lambda msg: write_string('[MGet Info] ' + str(msg))
trouble = lambda msg: write_string('WARNING: ' + str(msg))

class Default(object): pass

std = Default()
std.UA = "Mget/0.6.4 (Linux; Mac OS X; en-us)"
std.FUA = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0"

