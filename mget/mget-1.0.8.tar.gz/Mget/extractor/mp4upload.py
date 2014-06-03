#!/usr/bin/env python3

import re
from .common import InfoExtractor

class Mp4upload_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?mp4upload\.com/(?:.*)'
	_VIDEO_ID = r'^(?:https?://)?(?:www\.)?mp4upload\.com/embed-([a-z-A-Z-0-9]+)'
	_PATTERN = r'(?:https?://)?(?:www[0-9]\.)mp4upload\.com[^\s<>"]+[0-9]'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'mp4upload')
		data = self._get_webpage(url,client)
		url = self.findall_regex(self._PATTERN, str(data['webpage']), 'mp4upload')

		return {'url': url,
			'video_id': video_id,
			'filename': video_id}
