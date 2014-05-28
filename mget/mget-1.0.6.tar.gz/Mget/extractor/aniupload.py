#!/usr/bin/env python3

import re
from .common import InfoExtractor

class Aniupload_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?aniupload\.com/(?:.*)'
	_VIDEO_ID = r'^(?:https?://)?(?:www\.)?aniupload\.com/embed-([a-z-A-Z-0-9]+)'
	_PATTERN = r'(?:https?://)[^\s<>"]+aniupload\.com[^\s<>"]+'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'mp4upload')
		data = self._get_webpage(url,client)
		url = self.findall_regex(self.pattern, str(data['webpage']), 'aniupload')

		return {'url': url,
			'video_id': video_id,
			'filename': video_id}
