#!/usr/bin/env python3

import re
from .common import InfoExtractor

class Aniupload_IE(InfoExtractor):
	_VIDEO_ID = r'^(?:https?://)?(?:www\.)?aniupload\.com/embed-([a-z-A-Z-0-9]+)'
	_VIDEO_URL = r'^(?:https?://)?(?:www\.)?aniupload\.com/(?:.*)'
	_PATTERN =  r'(?:https?://)[^\s<>"]+aniupload\.com[^\s<>"]+'

	def _dl_url(self,url,client):
		if not re.match(self._VIDEO_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'aniupload')
		data = self._get_webpage(url,client)
		url = self.findall_regex(self._PATTERN, str(data['webpage']), 'aniupload')

		return {'url': url,
			'video_id': video_id,
			'filename': video_id}
