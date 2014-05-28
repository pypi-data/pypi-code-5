#!/usr/bin/env python3

import re
from .common import InfoExtractor

#url = http://anivids.tv/embed-elnm4ff5vdpr-650x370.html

class Anivids_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?anivids\.tv/(?:.*)'
	_VIDEO_ID = r'^(?:https?://)?(?:www\.)?anivids\.tv/embed-([a-z-A-Z-0-9]+)'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'anivids')
		data = self._get_webpage(url,client)
		d = self.search_regex('67,(.+?).split', str(data['webpage']), 'anivids')
		r = (d.split('|')[2:])

		ip = "%s.%s.%s.%s" %  (r[18],r[17],r[15],r[14])
		port = "%s" %  (r[13])
		key = "%s" % (r[25])
		filename = "%s" % ('v.'+r[24])

		return {'url': "http://%s:%s/%s/%s" % (ip,port,key,filename),
			'video_id': video_id,
			'filename': video_id}

