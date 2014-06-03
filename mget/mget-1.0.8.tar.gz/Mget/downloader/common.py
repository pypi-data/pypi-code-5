#!/usr/bin/env python3

import os, sys, time
from ..utils import common, urlparse

class FileDownloader(object):
	def __init__(self, info = {}):
		self.params = info
		self.last_len = 0

	@staticmethod
	def getLocalFilesize(filename):
		if not os.path.exists(filename): return None
		return os.stat(filename).st_size

	@staticmethod
	def EXFilename(filename):
		idx = 1
		dirname = '.'

		name, ext = filename.rsplit('.', 1)
		names = [x for x in os.listdir(dirname) if x.startswith(name)]
		names = [x.rsplit('.', 1)[0] for x in names]
		suffixes = [x.replace(name, '') for x in names]

		suffixes = [x[2:-1] for x in suffixes if x.startswith('-(') and x.endswith(')')]
		indexes  = [int(x) for x in suffixes if set(x) <= set('0123456789')]
		if indexes: idx += sorted(indexes)[-1]
		return ('%s-(%d).%s' % (name, idx, ext))

	@staticmethod
	def getFilename(url):

		fname = os.path.basename(urlparse.urlparse(url).path)
		if len(fname.strip(" \n\t.")) == 0: return None
		return urlparse.unquote_plus(fname)

	@staticmethod
	def getFilename_header(cdisp):
		if not cdisp: return None

		cdtype = cdisp.split(';')

		if len(cdtype) == 1: return None
		if cdtype[0].strip().lower() not in ('inline', 'attachment'): return None

		# several filename params is illegal, but just in case
		fnames = [x for x in cdtype[1:] if x.strip().startswith('filename=')]
		if len(fnames) > 1: return None
		name = fnames[0].split('=')[1].strip(' \t"')
		name = os.path.basename(name)
		if not name: return None
		return name

	def _progress_bar(self, s_dif = None, progress = None, bytes = None, dif = None, width = 50):
		term_width = common.get_term_width()
		width = term_width - width

		_res = ["%6s" % ("{0:.1f}%".format(float(progress) * 100.0)),
			"[" + "="*int(progress*width)+">" + " "*(width-int(progress*width)) + "]"
			"%10s" % ("{:02,}".format(self.cursize,self.filesize)),
			"%7s" % (self.calc_speed(dif,bytes)),
			"ETA: "+self.calc_eta(s_dif,bytes,self.cursize,self.filesize)]

		line = " ".join(["%s" % x for x in _res])
		if self.params.get('newline'): sys.stdout.write('\n')
		else:sys.stdout.write('\r')
		if self.last_len: sys.stdout.write('\b' * self.last_len)

		sys.stderr.write("\r")
		sys.stdout.write(line)
		sys.stdout.flush()
		self.last_len = width

	def get_progress(self):
		progress = float(self.cursize)/float(self.filesize)
		if progress < 0: progress = 0
		if progress > 1: progress = 1
		return progress

	def calc_speed(self, dif, bytes):
		if bytes == 0 or dif < 0.001: return "%10s" % ("--.-K/s")
		return "%10s" % ('%s/s' % (common.format_size(float(bytes) / dif, True)))

	def calc_eta(self, dif, bytes, current, total):
		if current == 0 or dif < 0.001: return '--:--:--'
		rate = float(current) / dif
		eta = int((float(total) - float(current)) / rate)
		return "%8s" % (common.format_time(eta))

