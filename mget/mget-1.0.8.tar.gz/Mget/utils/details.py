#!/usr/bin/env python3

import sys
import platform
from time import strftime, localtime
from http.client import responses
from . import common, write_string, report, trouble

L_TIME = "[%s]" % (strftime("%a,%d %b %Y %H:%M:%S IST", localtime()))
A_DONE = "Already Downloaded!"
U_PROTO = "\n\nUnknown Protocal found, Try with http://<url>/"
FILE_EXIST = "\nThe file is already fully retrieved; nothing to do.\n"

def init_(url = None, site = None, wpage = False):
	if not wpage: string = L_TIME + "[%s]" % site
	if wpage: string = L_TIME + " [%s] Downloading webpage" % (site)
	if url: string = "%s" % (url)
	write_string(string)

def _error(msg = None, status = None):
	err = []

	if status is not None:
		err.append(status)
		err.append(responses[status])
	if msg is not None: err.append(msg)

	res = ' '.join(['%s' % s for s in err])
	string = FILE_EXIST if status == 416 else '\n\nERROR: %10s' % (res)
	write_string(string)

def debug_info(info):
	report = []
	report.append("Python Version %s %s" % (platform.python_version(),common.platform_name()))
	report.append("Proxy map %s" % (info.get('proxy') or {}))

	write_string("\n".join("[debug] %s" % x for x in report))

def print_info(info, trying=None, dump_info=False, quiet_mode=False):
	result = []
	if trying: result.append("\n" + L_TIME + " Read error at byte [%s/%s] - Retrying (try: %s)"\
			% (trying,info.get('cursize'),info.get('filesize')))

	if quiet_mode:
		result.append("Filesize: [%s] -> %s\n" % \
				(int(info.get('filesize')),info.get('filename')))
		write_string("\n".join(["%s" % x for x in result]))
		return True
	if(info.get('proxy')): result.append("Proxy: %s" % (info.get('proxy')))

	status = info.get('status')
	b_size = info.get('filesize')
	f_size = common.format_size(info.get('filesize'))

	result.append("Status code: %s %s" % (status, responses[status]))

	B_size = ''; F_size = ''
	if info.get('resuming'):
		B_size = (int(info.get('filesize')) - int(info.get('cursize')))
		F_size = "["+common.format_size(B_size)+"] remaining"

	result.append("Filesize: %s [%s], %s %s [%s]" % (b_size,f_size,B_size,F_size,info['type']))

	if dump_info: 
		result.append("FileName: %s\n" % (info.get('filename')))
		write_string("\n".join(["[MGet Info] %s" % x for x in result]))

	else:
		result.append("Saving to: %s\n" % (info['filename']))
		write_string("\n".join(["[Download] %s" % x for x in result]))

def _quitting(filename, cursize, filesize):
	f_size = common.format_size(cursize)
	percent = "{0:.1f}%".format(float(cursize)/float(filesize) * 100.0)
	write_string("\n\nQuitting: ({}) {:02,} [{}]\n".format(percent,cursize,f_size))

def done_dl(speed,filename,cursize,filesize):
	if cursize > filesize: filesize = cursize
	percent = "{0:.1f}%".format(float(cursize)/float(filesize) * 100.0)
	string = "\n\n[MGet Info] %s at %s - [%s] %s/%s\n" % (filename,speed,percent,cursize,filesize)
	write_string(string)
