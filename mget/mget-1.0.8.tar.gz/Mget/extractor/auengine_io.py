#!/usr/bin/env python3

import re
from .common import InfoExtractor

class Auengine_io_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?auengine\.io/embed/(?:.*)'
	_VIDEO_ID = r'^(?:https?://)?([^\s<>"]+|www\.)?auengine\.io/embed/([a-z-A-Z-0-9]+)'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		video_id = self.search_regex(self._VIDEO_ID, url, 'videonest')
		data = self._get_webpage(url,client)
		url = self.findall_regex(r'file: \'(.+?)\'', str(data['webpage']), 'videonest')

		return {'url': url,
			'video_id': video_id,
			'filename': video_id}
