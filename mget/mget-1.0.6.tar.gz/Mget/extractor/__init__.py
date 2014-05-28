#!/usr/bin/env python3

__all__ = ['strip_site', 'get_url']

import re
from ..utils import details, std
from .common import InfoExtractor
from .anivids import Anivids_IE
from .aniupload import Aniupload_IE
from .auengine import Auengine_IE
from .mp4upload import Mp4upload_IE
from .trollvid import Trollvid_IE
from .videonest import Videonest_IE
from .yourupload import Yourupload_IE
from .xvideos import Xvideos_IE

_SITE_LIST = [	'mp4upload', 'trollvid', 'anivids',
		'xvideos', 'auengine', 'aniupload',
		'yourupload', 'videonest']
_ALL_CLASSES = [klass for name, klass in globals().items() if name.endswith('_IE')]

def gen_extractors():
	return [klass() for klass in _ALL_CLASSES]

def get_info_extractor(ie_name):
	return globals()[ie_name.capitalize()+'_IE']

def strip_site(url):
	m = re.match(r'(?:\w*://)?(?:.*\.)?([a-zA-Z-1-9]*\.)', url)
	c_url = m.groups()[0]
	return c_url[:-1]

def get_url(url,*args):
	site = strip_site(url)

	if args[1]:
		data = InfoExtractor._get_webpage(url,args[0])
		with open(site + '.html', 'w') as f:
			f.write(data['webpage'])
		exit("[%s] Webpage Downloaded" % (site.capitalize()))
	
	if site in _SITE_LIST:
		ie = get_info_extractor(site)
		info = ie()._dl_url(url, args[0])
		url = info.get('url') if info else None

	if url is None: exit(details._error('URL Error'))

	return url
