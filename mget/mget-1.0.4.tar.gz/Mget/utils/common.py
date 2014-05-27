#!/usr/bin/env python3

import os, sys
import urllib.parse as urlparse
from math import log

class FileDownloader(object):
	def __init__(self, mget = None):
		self.mget = mget

	@staticmethod
	def getLocalFilesize(filename):
		if not os.path.exists(filename): return None
		return os.stat(filename).st_size

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

def format_size(bytes, short=False):
	bytes = int(bytes)
	UNITS = [('B', 0), ('K', 0), ('M', 1)]

	if bytes > 1:
		exponent = min(int(log(bytes, 1024.0)), len(UNITS)-1)
		quotient = float(bytes) / float(1024 ** exponent)
		(unit, decimals) = UNITS[exponent]
		result = "{:.%sf}{}" % (decimals)

		return result.format(quotient, unit)

	else: return 'Unknown'

def format_time(duration):
	duration = int(duration)
	UNITS = [('s', 1), ('m', 60), ('h', 3600), ('d', 604800)]
	result = []

	if duration == 0: return '0 sec'
	for i in range(len(UNITS)-1,-1,-1):
		a = duration // UNITS[i][1]
		if a > 1:
			result.append((a, UNITS[i][0]))
			duration -= a * UNITS[i][1]

	return " ".join(["%s%s" % x for x in result[:1]])

def calc_speed(dif, bytes):
	if bytes == 0 or dif < 0.001: return "%10s" % ("--.-K/s")
	return "%10s" % ('%s/s' % (format_size(float(bytes) / dif, True)))

def calc_eta(dif, bytes, current, total):
	if current == 0 or dif < 0.01: return '%10s' % ('0 sec')
	rate = float(bytes) / dif
	eta = ((float(total) - float(current)) / rate)
	return "%10s" % (format_time(eta))

def best_block_size(est_time, bytes):
	new_min = max(bytes / 2.0, 1.0)
	new_max = min(max(bytes * 2.0, 1.0), 4194304)

	if est_time < 0.001: return int(new_max)

	rate = bytes / est_time

	if rate > new_max: return int(new_max)
	if rate < new_min: return int(new_min)

	return int(rate)

