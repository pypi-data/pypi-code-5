#!/usr/bin/env python3

import os
import ssl
import socket
from . import urllib, urlparse, cookiejar
from . import details, std

class Client(object):
	def __init__(self, proxy = None, timeout = 120.0, params = {}):
		self.timeout = timeout
		self.params = params

		self._setup_opener()

	def getInfos(self, url, filename, cursize):

		urlObj, req = self.urlopen(url, cursize)
		info = urlObj.headers

		return {'headers': info,
			'cookiejar': self.cookiejar,
			'urllibObj': urlObj,
			'request': req,
			'status': urlObj.getcode(),
			'filename': filename,
			'filesize': int(info.get('content-length', 0)) + int(cursize) or 8*1024,
			'type': info.get('content-type') or 'unknown'}

	def urlopen(self, url, cursize = 0, req_head = None, params = None):
		headers = {'User-Agent':self.params.get('user-agent') or std.UA, 'Accept':'*/*'}

		if req_head: headers.update(req_head)
		if cursize != 0: headers['Range'] = 'bytes=%s-' % (cursize)
		if params: params = urlparse.urlencode(params).encode('utf-8')

		url = urlparse.unquote(url)
		request = urllib.Request(url,headers=headers)

		try: urllibObj = self.opener.open(request, params)
		except urllib.HTTPError as e: details._error(status=e.code); exit()
		except urllib.URLError as e: details._error(e.reason); exit()
		except (socket.error, socket.timeout) as e: details._error(status=e); exit()

		return urllibObj, request

	def _setup_opener(self):
		cookiefile = self.params.get('cookiefile')
		proxy = self.params.get('proxy')

		if cookiefile is None: self.cookiejar = cookiejar.CookieJar()
		else:
			self.cookiejar = cookiejar.MozillaCookieJar(cookiefile)
			if os.access(cookiefile, os.R_OK): self.cookiejar.load()

		cookie_processor = urllib.HTTPCookieProcessor(self.cookiejar)
		if proxy: 
			if proxy == '': proxies = {}
			else: proxies = {'http':proxy,'https':proxy}
		else:
			proxies = urllib.getproxies()
			if 'http' in proxies and 'https' not in proxies:
				proxies['https'] = proxies['http']

		proxy_handler = urllib.ProxyHandler(proxies)
		https_handler = self.HTTPSHandler(no_check = True, debuglevel=0)
		self.opener = urllib.build_opener(https_handler,proxy_handler,cookie_processor)
		self.opener.addheaders = []
		urllib.install_opener(self.opener)
		socket.setdefaulttimeout(self.timeout)

	def HTTPSHandler(self, no_check, **kwargs):
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
		context.verify_mode = (ssl.CERT_NONE if no_check else ssl.CERT_REQUIRED)
		context.set_default_verify_paths()
		try:context.load_default_certs()
		except:pass

		return urllib.HTTPSHandler(context=context, **kwargs)
