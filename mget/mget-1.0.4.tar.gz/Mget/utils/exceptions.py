#!/usr/bin/env python3

class ExtractorError(Exception): pass

class RegexNotFoundError(ExtractorError): pass

class DownloadError(Exception):
	def __init__(self, msg, exc_info=None):
		super(DownloadError, self).__init__(msg)
		self.exc_info = exc_info

class UnavailableVideoError(Exception): pass

