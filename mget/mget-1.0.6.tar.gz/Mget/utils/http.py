#!/usr/bin/env python3

import os, sys, socket
import subprocess
from time import time,sleep
from . import common, details

class HTTPDownloader(object):
	def __init__(self, urlObj, fileObj, info):
		self.params = info
		self.urlObj = urlObj
		self.fileObj = fileObj
		self.filename = info['filename']
		self.cursize = int(info['cursize'])
		self.filesize = int(info['filesize'])
		self.chunk = info.get('buffersize', 1) * 1024
		self.quit_size = info.get('quitsize', 100.0)

	def start(self):
		self.start_time = time()
		while True:
			if self.quit_size != 100.0:
				if self.get_progress() * 100.0 >= self.quit_size:break
			if self.cursize == self.filesize:break

			get_time = time()
			buffer = self.urlObj.read(self.chunk)
			end_time = time()

			if len(buffer) == 0:break

			try:self.fileObj.write(buffer)
			except (IOError, OSError) as err: details._error(err); return False

			self.cursize += len(buffer)
			if self.params.get('buffersize') == 1 and not self.params.get('noresize'):
				self.chunk = common.best_block_size(end_time-get_time,len(buffer))
			self._progress_bar(self.get_progress(),len(buffer),time()-get_time)
		return True

	def _progress_bar(self, progress = None, bytes = None, dif = None, width = 55):

#		width = self.term_width() - width
		_res = ["{0:.1f}%".format(float(progress) * 100.0),
			"[" + "="*int(progress*width)+">" + " "*(width-int(progress*width)) + "]"
			"%20s" % ("{:02,} / {:02,}".format(self.cursize,self.filesize)),
			"ETA: "+common.calc_eta(dif,bytes,self.cursize,self.filesize)]

		if self.params.get('newline'): sys.stdout.write('\n')
		else:sys.stdout.write('\r')

		sys.stdout.flush()
		sys.stdout.write(" ".join(["%s" % x for x in _res]))
		sys.stdout.flush()

	def get_progress(self):
		progress = float(self.cursize)/float(self.filesize)
		if progress < 0: progress = 0
		if progress > 1: progress = 1
		return progress

	def term_width(self):
		columns = os.environ.get('COLUMNS', None)
		if columns: return int(columns)

		try:
			sp = subprocess.Popen(['stty', 'size'],\
				stdout = subprocess.PIPE,\
				stderr = subprocess.PIPE)
			out, err = sp.communicate()
			return int(out.split()[1])
		except: pass
		return None

