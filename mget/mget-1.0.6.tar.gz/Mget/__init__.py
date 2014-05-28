#!/usr/bin/env python3

__all__ = ['mget','utils','extractor']

__version__ = 'version 1.0.6'

import os
from . import mget
from .utils import details
from argparse import ArgumentParser, HelpFormatter

def Arguments():
	usage = '\tmget [options..] URL [URL..]'
	epilog = 'Download file with an ease!'
	args = {'usage':usage, 'prog':'mget', 'epilog':epilog}
	parser = ArgumentParser(**args)
	HelpFormatter(parser,max_help_position=120)

	genr = parser.add_argument_group('General arguments')
	down = parser.add_argument_group('Download arguments')
	verb = parser.add_argument_group('Simulate arguments')
	fsys = parser.add_argument_group('Filesystem arguments')

	parser.add_argument('-V', '--version', action='version', version='%(prog)s '+ __version__)

	genr.add_argument('-e', '--extractors', dest='extractors', action='store_true', help="Print supported Video sharing sites.")
	genr.add_argument('-m', dest='mirror', action='store_true', help="Download from mirror link.")
	genr.add_argument('-c', dest='continue_dl', action='store_true', help="Fource to resume download.")
	genr.add_argument('-q', dest='quitsize', metavar='PERCENT', type=float, default=100.0, help="How much percent to download default: (100.0).")
	genr.add_argument('-U', dest='useragent', metavar='USER-AGENT', type=str, help="User Agent to use.")

	down.add_argument('--no-resize-buffer', dest='noresize', action='store_true', help="Do not resize the downloading buffer size.")
	down.add_argument('--buffer', dest='buffersize', metavar='SIZE', type=int, default=1, help="Download buffer size (e.g. 1 - 16) default 1 [1024].")
	down.add_argument('--proxy', dest='proxy', metavar='PROXY', type=str, help="Use the specified HTTP/HTTPS proxy.")

	verb.add_argument('-g', '--get-url', dest='geturl', action='store_true', help="Print Download url and exit.")
	verb.add_argument('-j', '--dump-json', dest='dump', action='store_true', help="simulate, quiet but print information.")
	verb.add_argument('--newline', dest='newline', action='store_true', help="output progress bar as new lines.")
	verb.add_argument('--write-pages', dest='wpage', action='store_true', help="Write downloaded pages to files in the current directory to debug.")

	fsys.add_argument('--cookies', dest='cookiefile', metavar='FILE', type=str, help="Cookie file to use when connecting.")
	fsys.add_argument('-i', dest='urlfile', metavar='FILE', type=open, help="File with list of url to download.")
	fsys.add_argument('-O', dest='filename', metavar='FILENAME', type=str, help="File name to save the output.")

	opts, args = parser.parse_known_args()
	return parser, opts, args

def check_args(opts):
	if os.name != 'posix': details._error(action="MGet works only on Linux!"); exit(1)
	if opts.geturl and opts.dump: details._error(action="cannot use (-g, -j) togather"); exit(1)
	if opts.extractors:
		from .extractor import _SITE_LIST
		sites = "\n".join('%s' % s for s in _SITE_LIST)
		details.write_string(sites)
		exit(1);

def main():
	urls = []
	parser, opts, args = Arguments()
	check_args(opts)

	info = {
	'proxy'		: opts.proxy,
	'quitsize'	: opts.quitsize,
	'buffersize'	: opts.buffersize,
	'newline'	: True if opts.newline else False,
	'noresize'	: True if opts.noresize else False,
	'cookiefile'	: opts.cookiefile,
	'urlfile'	: opts.urlfile,
	'continue'	: opts.continue_dl}

	if len(args) < 1: parser.print_usage()
	if opts.urlfile : urls = [x.strip() for x in opts.urlfile.readlines()]

	urls = [url.strip() for url in (urls + args)]

	for url in urls:
		if url.startswith('-'): details._error('Option not available'); exit(1)
		opts.url = url if url.startswith('http') else ('http://%s' % (url))
		try: down = mget.MGet(opts,info); down.start()
		except KeyboardInterrupt: details._error('Interrupted by user')

