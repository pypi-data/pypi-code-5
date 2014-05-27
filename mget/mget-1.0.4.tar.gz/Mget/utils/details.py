#!/usr/bin/env python3

import sys
from . import common
from time import strftime, localtime
from http.client import responses

L_TIME = "[%s]" % (strftime("%a,%d %b %Y %H:%M:%S IST", localtime()))
A_DONE = "Already Downloaded!"
U_PROTO = "Unknown Protocal found, Try with http://<url>/"
FILE_EXIST = "\nThe file is already fully retrieved; nothing to do.\n"

def write_string(s, out = None):
	if out is None: out = sys.stderr
	assert type(s) == str

	out.write(s+"\n")
	out.flush()

def report(msg): write_string(msg)
def _get_url(url): write_string("[MGet URL] " + url)

def init_(url = None, site = None, mirror = False):
	if mirror: string = L_TIME
	if site and not mirror: string = L_TIME + " [%s] Downloading webpage" % (site)
	if url: string = "[Download] %s" % (url)
	write_string(string)

def _error(msg = None, status = None):
	err = []

	if status is not None:
		err.append(status)
		err.append(responses[status])
	if msg is not None: err.append(msg)

	res = ' '.join(['%s' % s for s in err])
	string = FILE_EXIST if status == 416 else '\nERROR: %10s' % (res)
	write_string(string)

def dump_info(info):
	result = []
	if(info['proxy']): result.append("Proxy: %s" % (info['proxy']))

	status = info['status']
	b_size = info['filesize']
	f_size = common.format_size(info['filesize'])

	result.append("Status code: %s %s" % (status, responses[status]))

	B_size = ''; F_size = ''
	if info['resuming']:
		B_size = (int(info['filesize']) - int(info['cursize']))
		F_size = "["+common.format_size(B_size)+"]"

	result.append("Filesize: %s [%s], %s %s [%s]" % (b_size,f_size,B_size,F_size,info['type']))
	result.append("FileName: %s\n" % (info['filename']))

	write_string("\n".join(["[MGet Info] %s" % x for x in result]))

def start(info):
	result = []
	if(info['proxy']): result.append("Proxy: %s" % (info['proxy']))

	status = info['status']
	b_size = info['filesize']
	f_size = common.format_size(info['filesize'])

	result.append("Status code: %s %s" % (status, responses[status]))

	B_size = ''; F_size = ''
	if info['resuming']:
		B_size = (int(info['filesize']) - int(info['cursize']))
		F_size = "["+common.format_size(B_size)+"]"

	result.append("Filesize: %s [%s], %s %s [%s]" % (b_size,f_size,B_size,F_size,info['type']))
	result.append("Saving to: %s\n" % (info['filename']))

	write_string("\n".join(["[Download] %s" % x for x in result]))

def trying(trying,current,filename):
	write_string(L_TIME + " Read error at byte [%s/%s] Retrying" % (current, filename))
	wriet_string(L_TIME + " (try: %s)" % (trying))

def _quitting(filename, filesize):
	b_size = common.FileDownloader.getLocalFilesize(filename)
	f_size = common.format_size(b_size)
	percent = "{0:.1f}%".format(float(b_size)/float(filesize) * 100.0)
	write_string("\n\nQuitting: ({}) {:02,} [{}]\n".format(percent,b_size,f_size))

def done_dl(speed,filename,cursize,filesize):
	percent = "{0:.1f}%".format(float(cursize)/float(filesize) * 100.0)
	string = "\n\n[Download] %s at %s - [%s] %s/%s\n" % (filename,speed,percent,cursize,filesize)
	write_string(string)
