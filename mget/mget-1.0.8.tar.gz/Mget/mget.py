#!/usr/bin/env python3

import os, sys
import time
import socket
from .utils import *
from .extractor import *
from .downloader import *

class MGet(FileDownloader):
	def __init__(self, opts, info):
		FileDownloader.__init__(self)

		if opts.verbose: details.debug_info(info)
		self.info = info
		self.params = opts
		self.client = client.Client(info=self.info)
		self.ie_result = get_info(opts.url,self.client,info)
		self.url = self.ie_result.get('url', opts.url)
		self.filename = self.params.filename or\
				self.getFilename(self.url) or info.get('def_page')
		self.cursize = self.getLocalFilesize(self.filename) or 0
		self.quitsize = self.params.quitsize
		self.mode = 'wb' if self.cursize == 0 else 'ab'
		self.trying = 0

	def __downloadFile__(self, urlObj):
		start = info['start_time'] = time.time()
		try:
			with open(self.filename, self.mode) as fileObj:
				dl = MGetDownloader(urlObj,fileObj,info)
				try: dl.start()
				except (socket.timeout, socket.error) as err:
					details._error("\n"+err)
					self.__retry__()
					return False
		except KeyboardInterrupt:
			self.cursize = self.getLocalFilesize(self.filename)
			details._quitting(self.filename,self.cursize,info.get('filesize'))
			return False
		except (IOError, OSError, TypeError, DownloadError) as err:
			self.cursize = self.getLocalFilesize(self.filename)
			if self.info.get('debug_mget'): details._error(err)
			else: details._quitting(self.filename,self.cursize,info.get('filesize'))
			return False
		finally:
			if self.params.cookiefile: self.cookiejar.save()
			self.cursize = self.getLocalFilesize(self.filename)
			urlObj.close()

		if self.cursize < self.filesize and not info.get('quitsize'):
			details.report('Expected: %s, Recived: %s' % (info.get('filesize'),self.cursize))

		_opts= {'speed': self.calc_speed(time.time()-start, self.cursize-info['cursize']),
			'filename': self.filename,
			'cursize': self.cursize,
			'filesize': info.get('filesize')}

		details.done_dl(**_opts)
		return True

	def __retry__(self):
		self.trying += 1
		self.cursize = self.getLocalFilesize(self.filename)

		if self.cursize != info.get('filesize'): return self.resume()

	def resume(self):
		if self.cursize != info.get('cursize'):
			info['cursize'] = self.cursize
			info.update(self.client.getInfos(self.url, self.filename, self.cursize))
			details.print_info(info,self.trying)

		return self.__downloadFile__(info.get('urllibObj'))

	def start(self):
		global info
		if self.info.get('restart'): self.cursize = 0; self.mode = 'wb'
		if self.params.geturl: details.report(self.url); return True
		if os.path.exists(self.filename) and not self.info.get('continue'):
			self.filename = self.EXFilename(self.filename)
			self.cursize = self.getLocalFilesize(self.filename) or 0

		details.init_(url=self.url)
		info = self.client.getInfos(self.url, self.filename, self.cursize)	

		if not info: return False

		info['cursize'] = self.cursize
		info['resuming'] = True if self.cursize != 0 else False
		info.update(self.info)

		file_header = lambda cdisp: self.getFilename_header(cdisp) or info['filename']
		if not self.params.filename: 
			cdisp = info.get('headers').get('Content-Disposition')
			self.filename = info['filename'] = file_header(cdisp)

		if self.params.write_info: common.write_info(info)
		if self.params.dump_info: details.print_info(info, dump_info=True); return True
		else: details.print_info(info,quiet_mode=self.params.quiet_mode)

		if self.params.quitsize:
			progress = float(self.cursize)/float(info.get('filesize'))*100.0
		if progress and progress >= self.params.quitsize:
			details._error(details.FILE_EXIST)
			return True

		self.cookiejar = info.get('cookiejar')
		if os.path.exists(self.filename) and info.get('continue'): return self.resume()

		return self.__downloadFile__(info.get('urllibObj'))

	def __exit__(self, *args):
		if self.params.cookiefile: self.cookiejar.save()
