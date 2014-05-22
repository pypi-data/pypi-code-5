import os
import itertools
from django.core.files.storage import Storage
from django.conf import settings
from urlparse import urljoin
from imsto_client import ImstoClient

MIN_PATH_LEN = 28

def load_imsto():
	host = settings.IMSTO_HOST
	roof = settings.IMSTO_ROOF
	client = ImstoClient(host, roof)
	return client

def imsto_url(name, size='orig', base_url = ""):
	"""Returns an absolute URL where the file's contents can be accessed
	directly by a web browser.
	"""

	if name is None or name == '':
		return ''

	if len(name) > MIN_PATH_LEN and name[2] == name[5] == '/':

		url_prefix = settings.IMSTO_URL_PREFIX
		thumb_path = settings.IMSTO_THUMB_PATH
		return '{}/{}/{}/{}'.format(url_prefix.rstrip('/'), thumb_path.strip('/'), size, name)

	return urljoin(base_url, name).replace('\\', '/')


class ImageStorage(Storage):
	"""A custom storage backend to store files in GridFS

		to use this backend, change your settings.py:

			DEFAULT_FILE_STORAGE = 'imsto_client.django.ImageStorage'

	"""

	def __init__(self, base_url=None):

		if base_url is None:
			base_url = settings.MEDIA_URL
		self.base_url = base_url
		self.imsto = load_imsto()
		self.field = 'image_path'

	def delete(self, name):
		"""Deletes the specified file from the storage system.
		TODO:
		"""
		pass

	def exists(self, name):
		"""Returns True if a file referened by the given name already exists in the
		storage system, or False if the name is available for a new file.
		"""
		pass

	def listdir(self, path=None):
		"""Lists the contents of the specified path, returning a 2-tuple of lists;
		the first item being directories, the second item being files.
		"""
		pass

	def size(self, name):
		"""Returns the total size, in bytes, of the file specified by name.
		"""
		pass

	def url(self, name, size='orig'):
		"""Returns an absolute URL where the file's contents can be accessed
		directly by a web browser.
		"""
		return imsto_url(name, size, self.base_url)

	def _open(self, name, mode='rb'):
		pass

	def get_available_name(self, name):
		"""Returns a filename that's free on the target storage system, and
		available for new content to be written to.
		"""
		print 'src name: %s' % name
		return os.path.basename(name)


	def _save(self, name, content):
		print 'available name: %s' % name
		print 'type of content: %s' % type(content)
		print 'type of content.file: %s' % type(content.file)
		if hasattr(content, 'temporary_file_path'):
			file = content.temporary_file_path()
			print 'temp file: %s' % file
		r, id, filename = self.imsto.store(content.file,name=name)

		if r:
			print 'stored {}, {}, {}'.format(r, id, filename)
			return filename

		print 'store failed, name: %s' % name
		return None

