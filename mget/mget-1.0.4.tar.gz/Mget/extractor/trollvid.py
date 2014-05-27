#!/usr/bin/env python3

UID = "dd274cdecf4682b0d121bd7110d634a191399348669978"
GA = "GA1.2.671399275.1399359262"
CF_KEY = "b31505327a1b445a98e4ca5b0554fa7e4defd624-1400241478-86400"

cookie =  "__cfduid=%s; cf_clearance=%s;_ga=%s" % (UID,CF_KEY,GA)

import re
from .common import InfoExtractor
from ..utils import std

class Trollvid_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?trollvid\.com/(?:.*)'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'trollvid')
		data = self._get_webpage(url,client,Req_head = {'User-Agent':std.FUA,'Cookie':cookie})
		url = self.findall_regex(r'http%3A%2F%2F[^\s<>"]+', str(data))

		urllibObj, req = client.urlopen(url[0])
		return {'url': urllibObj.geturl(),
			'video_id': video_id,
			'filename': video_id}

