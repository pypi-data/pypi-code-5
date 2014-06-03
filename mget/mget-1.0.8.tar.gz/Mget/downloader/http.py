#!/usr/bin/env python3

import time
from . import FileDownloader
from ..utils import common, details, DownloadError

class MGetDownloader(FileDownloader):
	def __init__(self, urlObj, fileObj, info):
		FileDownloader.__init__(self,info)
		self.info = info
		self.urlObj = urlObj
		self.fileObj = fileObj
		self.start_time = info.get('start_time')
		self.filename = info.get('filename')
		self.cursize = int(info.get('cursize'))
		self.filesize = int(info.get('filesize'))
		self.chunk = info.get('buffersize', 1) * 1024
		self.quit_size = info.get('quitsize', 100.0)

	def start(self):
		while True:
			if self.quit_size != 100.0:
				if self.get_progress() * 100.0 >= self.quit_size: break
			if self.cursize == self.filesize: break

			get_time = time.time()
			try: buffer = self.urlObj.read(self.chunk if self.chunk > 1024 else 1024)
			except: raise DownloadError("Download error")
			end_time = time.time()

			if len(buffer) == 0: break

			self.fileObj.write(buffer)
			self.cursize += len(buffer)
			if self.info.get('buffersize') == 1 and not self.info.get('noresize'):
				self.chunk = common.best_block_size(end_time - get_time, len(buffer))

			self._progress_bar(**{  's_dif': time.time() - self.start_time,
						'progress': self.get_progress(),
						'bytes': len(buffer),
						'dif': end_time - get_time})
		return True

