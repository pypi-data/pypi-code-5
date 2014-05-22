

import os
import urllib
from httplib2 import Http
from urllib import urlencode
import json
import time
from _util import encode_upload

__all__ = [
	'ImstoClient',
]

TOKEN_TIMEOUT = 15

class ImstoClient(object):
	"""ImstoClient"""
	def __init__(self, host, roof = '', app='0', uid='0'):
		self.host = host
		self._roof = roof
		self._token = ''
		self._app=app
		self._uid=uid
		self._last_stamp = 0

	def _request(self, url, method = 'GET', body = None, headers = None):
		print '_request: %s: %s' % (method, url)
		h = Http()
		if method == 'POST':
			if headers is None:
				headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' }
			resp, content, = h.request(url, method, body=body, headers=headers)
		else:
			resp, content = h.request(url, method)

		print 'resp: %s' % resp
		# print 'body: %s' % content
		try:
			if resp.status >= 400:
				print 'request error: {} {}'.format(resp.status, resp.reason)
				print 'response: {}'.format(content)
				return resp.status, resp.reason, json.loads(content) if content.startswith('{') else content
			if resp['content-type'] == 'application/json' or resp.status == 201 and resp['content-type'] == 'text/plain; charset=utf-8':
				return resp.status, resp.reason, json.loads(content)
			# get content
			return resp['content-type'], int(resp['content-length']), content
		except Exception, e:
			print e
			# print resp
			return resp.status, e, None

	def _url(self, node = ''):
		return 'http://{}/imsto/{}'.format(self.host, node)

	def roof():
		doc = "The roof property."
		def fget(self):
			return self._roof
		def fset(self, value):
			self._roof = value
		def fdel(self):
			del self._roof
		return locals()
	roof = property(**roof())

	def baseArgs(self):
		return dict(roof=self.roof,app=self.app,user=self.uid)

	@property
	def app(self):
		return self._app

	@app.setter
	def app(self, value):
		self._app = str(value)

	@property
	def uid(self):
		return self._uid

	@uid.setter
	def uid(self, value):
		self._uid = str(value)

	def getToken(self, app = 0, uid = 0):
		now = int(time.time())
		if self._token != '' and (self._last_stamp + TOKEN_TIMEOUT) > now:
			return self._token;

		body = urlencode(self.baseArgs())
		# print body
		first, second, result = self._request(self._url('token'), 'POST', body=body)
		# print result
		if isinstance(result, dict) and result['status'] == 'ok':
			self._token = result['token']
			self._last_stamp = now
		else:
			print 'request token error: %s' % second
		return self._token

	def store(self, file = None, content = None, name = None, content_type = None):
		token = self.getToken()
		# print 'token: %s' % token
		ext_data = self.baseArgs()
		ext_data['token'] = token
		content_type, body = encode_upload(file=file, content=content, name=name, content_type=content_type, ext_data=ext_data.items())
		headers = { 'Content-Type': content_type }
		first, second, res = self._request(self._url(), 'POST', body=body, headers=headers)
		# print type(res)
		print res
		if isinstance(res, dict):
			ret = res['status'] == 'ok'
			item = res['data'][0]
			if item.has_key('error'):
				raise Exception(item['error'])
				# return False, item['error']
			return ret, item['id'], item['path']

		print 'resp: %s, %s' % (first, second)
		return False, '', ''




if __name__ == '__main__':
	client = ImstoClient('localhost:8964', roof='demo')
	token = client.getToken()
	print token
	time.sleep(2)
	token = client.getToken()
	print token
