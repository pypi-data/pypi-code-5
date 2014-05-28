#!/usr/bin/env python3

import lxml.html, zlib, re
from io import StringIO
from ..utils import client,details,urlparse

class InfoExtractor(object):
	@staticmethod
	def _get_webpage(url,client,Req_head = None):
		headers= {'Accept-Encoding':'gzip,deflate'}
		if Req_head: headers.update(Req_head)

		urllibObj, req = client.urlopen(url, req_head=headers)

		return {'webpage': InfoExtractor.decompress(urllibObj),
			'urllibObj': urllibObj,
			'request': req}

	@staticmethod
	def decompress(urlObj):
		if urlObj.info().get('Content-Encoding') == 'gzip':
			data = urlObj.read()
		
			d = zlib.decompressobj(16+zlib.MAX_WBITS)
			data = d.decompress(data)
			return data.decode('utf-8')
		else: return urlObj.read().decode('utf-8')

	@staticmethod
	def search_regex(pattern, string, name, flags=0):
		mObj = re.search(pattern, string, flags)
		if mObj: return next(s for s in mObj.groups()if s is not None)
		else: details._error('unable to extract %s' % name)
		return None

	@staticmethod
	def findall_regex(pattern, string, name):
		mObj = re.findall(pattern, string)
		if mObj: return next(s for s in mObj if s is not None)
		else: details._error('unable to extract %s' % name)
		return None

	@staticmethod
	def get_param(url, param):
		query = urlparse.urlparse(url).query
		query = query.split('&')
		for i in query:
			if i.startswith(str(param + '=')): return i.split('=')[1]
		return None

