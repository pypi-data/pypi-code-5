#!/usr/bin/env python3

import re
from .common import InfoExtractor
from ..utils import urlparse
from .auengine_io import Auengine_io_IE

class Auengine_IE(InfoExtractor):
	_VALID_URL = r'^(?:https?://)?(?:www\.)?auengine\.com/(?:.*)'
	_VALID_URL_1 = r'^(?:https?://)?(?:www\.)?auengine\.io/embed/(?:.*)'

	def _dl_url(self,url,client):
		if re.match(self._VALID_URL_1, url): return Auengine_io_IE()._dl_url(url,client)
		if not re.match(self._VALID_URL, url): return None
		query = urlparse.urlparse(url).query
		query = query.split('&')
		for i in query:
			if i.startswith('file='): video_id = i.split('=')[1]

		return {'url': 'http://s45.auengine.com/videos/%s.mp4' % (video_id),
			'video_id': video_id,
			'filename': video_id}
