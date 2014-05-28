

import re
import urllib.parse as urlparse
from .common import InfoExtractor

class Xvideos_IE(InfoExtractor):
	_VALID_URL = "^(?:https?://)?(?:www\.)?xvideos\.com/video([0-9]+)(?:.*)"
	_PATTERN = r'https?://[^\s<>"]+|www\.[^\s<>"]+'

	def _dl_url(self,url,client):
		if not re.match(self._VALID_URL, url): return None
		data = self._get_webpage(url,client)
		urls = self.search_regex(r'flv_url=(.+?)&', str(data['webpage']), 'xvideos')
		url = self.findall_regex(_PATTERN, urls, 'xvideos')
#		video_title = re.search( r'<title>(.*?)\s+-\s+XVID', str(data['webpage']))

		return {'url': url}
