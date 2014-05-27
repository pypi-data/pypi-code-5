#!/usr/bin/env python3

import os
import sys
import time
import socket
from .extractor import *
from .utils import *

class MGet(FileDownloader):
	def __init__(self, args, info):
		FileDownloader.__init__(self)

		details.init_(site=strip_site(args.url),mirror=args.mirror)
		self.client = client.Client(params={
						'cookiefile': args.cookiefile,
						'proxy': args.proxy,
						'user-agent': args.useragent})
		self.url = get_url(args.url,self.client,args.wpage) if not args.mirror else args.url
		self.info = info
		self.params = args
		self.filename = self.params.filename or self.getFilename(self.url) or 'index.html'
		self.cursize = self.getLocalFilesize(self.filename) or 0
		self.quitsize = self.params.quitsize
		self.mode = 'wb' if self.cursize == 0 else 'ab'
		self.trying = 0

	def __downloadFile__(self, urlObj):
		start = time.time()
		try:
			with open(self.filename, self.mode) as fileObj:
				dl = HTTPDownloader(urlObj,fileObj,info)
				try: dl.start()
				except (socket.timeout, socket.error) as err:
					details._error(err)
					self.__retry__()
		except (IOError, OSError) as err:
			details._error(err)
			return False
		except KeyboardInterrupt:
			details._quitting(self.filename, info['filesize'])
			return False
		finally:
			self.cursize = self.getLocalFilesize(self.filename)
			urlObj.close()

		_opts= {'speed': common.calc_speed(time.time()-start, self.cursize-info['cursize']),
			'filename': self.filename,
			'cursize': self.cursize,
			'filesize': info['filesize']}

		details.done_dl(**_opts)
		return True

	def __retry__(self):
		self.trying += 1
		self.cursize = self.getLocalFilesize(self.filename)
		details.trying(self.trying, self.cursize, self.filename)

		if self.cursize != info['filesize']: return self.resume()

	def resume(self):
		if self.cursize != info['cursize']:
			info['cursize'] = self.cursize

			info['urllibObj'], info['request'] = \
			self.client.urlopen(self.url, self.cursize)

		return self.__downloadFile__(info['urllibObj'])

	def start(self):
		if self.params.geturl: details._get_url(self.url); return True
		details.init_(url=self.url)

		global info
		info = self.client.getInfos(self.url, self.filename, self.cursize)
		info['cursize'] = self.cursize
		info['resuming'] = True if self.cursize != 0 else False
		info.update(self.info)

		info['filename'] = self.getFilename_header(info['headers'].get("Content-Disposition", None)) or info['filename']

		if self.params.dump: details.dump_info(info); return True
		else: details.start(info)

		if self.params.quitsize: progress = float(self.cursize)/float(info['filesize'])*100.0
		if progress and progress >= self.params.quitsize:
			details._error("Already Downloaded {0:.1f}%".format(progress))
			return True

		if os.path.exists(self.filename) or info['continue']: return self.resume()

		return self.__downloadFile__(info['urllibObj'])

	def __exit__(self, *args):
		if self.params.cookiefile: cookiejar.save()
