#!/usr/bin/env python3

import os, sys
import locale
import platform
import subprocess
from math import log
from . import urlparse, report, trouble

def pref_encoding():
	try: pref = locale.getpreferredencoding(); u'TEST'.encode(pref)
	except: pref = 'UTF-8'

	return pref

def format_size(bytes, short=False):
	bytes = int(bytes)
	UNITS = [('B', 0), ('K', 2), ('M', 2)]

	if bytes > 1:
		exponent = min(int(log(bytes, 1024.0)), len(UNITS)-1)
		quotient = float(bytes) / float(1024 ** exponent)
		(unit, decimals) = UNITS[exponent]
		result = "{:.%sf}{}" % (decimals)

		return result.format(quotient, unit)

	else: return 'Unknown'

def format_time(duration):
	(mins, secs) = divmod(duration, 60)
	(hours, mins) = divmod(mins, 60)
	if hours > 99: return '--:--:--'
	elif hours == 0: return '00:%02d:%02d' % (mins, secs)
	else: return '%02d:%02d:%02d' % (hours, mins, secs)


def best_block_size(est_time, bytes):
	new_min = max(bytes / 2.0, 1.0)
	new_max = min(max(bytes * 2.0, 1.0), 4194304)

	if est_time < 0.001: return int(new_max)

	rate = bytes / est_time

	if rate > new_max: return int(new_max)
	if rate < new_min: return int(new_min)

	return int(rate)

def get_term_width():
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

def platform_name():
	result = platform.platform()
	if isinstance(result, bytes):
		result = result.decode(pref_encoding())

	assert isinstance(result, str)
	return result

def write_info(info):
	result = []

	result.append("\n".join("%s" % x for x in info.get('report')))
	result.append("Python Version %s %s\n" % (platform.python_version(),platform_name()))
	result.append("Default Url\t: %s" % info.get('defurl'))
	result.append("Url\t\t: %s" % info.get('url'))
	result.append("Proxy\t\t: %s" % ({} if info.get('proxy') == None else info.get('proxy')))
	result.append("Status\t\t: %s" % info.get('status'))
	result.append("Type\t\t: %s" % info.get('type'))
	result.append("Filename\t: %s" % info.get('filename'))
	result.append("Filesize\t: %s" % info.get('filesize'))
	result.append("Headers\t\t: %s" % (dict(info.get('headers'))))

	data = "\n".join("%10s" % x for x in result)
	with open(info.get('log_file'), 'w') as f:
		f.write(data)
		report('Done Writting information to %s\n' % info.get('log_file'))
	return True
