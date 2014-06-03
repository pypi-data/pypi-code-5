#!/usr/bin/env python3

import sys
import socket
import  traceback
from . import urllib

class ExtractorError(Exception):
	def __init__(self, msg, tb=None, excepted=False, cause=None):
		if sys.exc_info()[0] in (urllib.URLError, socket.timeout): excepted = True
		if not excepted:
			msg = msg + 'please report this issue to r4v0n3@gmail.com . Be sure to call mget with the --verbose flag and include its complete output. Make sure you are using the latest version.'

		super(ExtractorError, self).__init__(msg)
		self.traceback = tb
		self.exc_info = sys.exc_info()
		self.cause = cause

	def format_trace(self):
		if self.traceback is None: return None
		return ''.join(traceback.format_tb(self.traceback))

class DownloadError(Exception):
	def __init__(self, msg, exc_info=None):
		super(DownloadError, self).__init__(msg)
		self.exc_info = exc_info

