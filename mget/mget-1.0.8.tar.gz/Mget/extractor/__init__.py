#!/usr/bin/env python3

__all__ = ['get_info']

import re
from ..downloader import FileDownloader
from ..utils import std, common, details, urlparse
from .common import InfoExtractor
from .anivids import Anivids_IE
from .aniupload import Aniupload_IE
from .auengine import Auengine_IE
from .mp4upload import Mp4upload_IE
from .trollvid import Trollvid_IE
from .videonest import Videonest_IE
from .videodrive import Videodrive_IE
from .yourupload import Yourupload_IE

_SITE_LIST = [	'mp4upload.com', 'trollvid.net', 'anivids.tv', 'auengine.com', 'auengine.io',
		'aniupload.com', 'yourupload.com', 'videonest.net', 'videodrive.tv']
_ALL_CLASSES = [klass for name, klass in globals().items() if name.endswith('_IE')]

def gen_extractors():
	return [klass() for klass in _ALL_CLASSES]

def get_info_extractor(ie_name):
	return globals()[ie_name.capitalize()+'_IE']

def strip_site(url):
	hostname = re.match(r'(?:\w*://)?(?:.*\.)?([a-z-A-Z-0-9]*\.([a-z]*))', url).groups()[0]
	site = hostname.split('.')[0]
	return hostname, site

def get_info(url, client, info):
	hostname, site = strip_site(url)
	ret = {'url': url}
	details.init_(site=site,wpage=info.get('wpage'))

	if info.get('mirror'): return ret
	if info.get('wpage'):
		data = InfoExtractor._get_webpage(url,client)
		with open(site + '.html', 'w') as f:
			f.write(data['webpage'])
		details.report(' %s: Page written to %s.html' % (site,site))

	result = None
	if hostname in _SITE_LIST:
		ie = get_info_extractor(site)
		try: result = ie()._dl_url(url,client)
		except ExtractorError as err: details._error(err)

	if result is None or result.get('url') is None: return ret

	return result
