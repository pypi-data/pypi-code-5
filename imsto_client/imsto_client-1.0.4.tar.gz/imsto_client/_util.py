import os

__all__ = [
	'encode_upload', 
]

BOUNDARY = '----------bundary------'
CRLF = '\r\n'
#print CRLF

def encode_upload(file=None, content=None, name=None, content_type=None, ext_data=[]):
	"""encode a upload file form
		sea also: http://mancoosi.org/~abate/upload-file-using-httplib
	"""
	body = []
	# Add the metadata about the upload first
	for key, value in ext_data:
		body.extend(
		  ['--' + BOUNDARY,
		   'Content-Disposition: form-data; name="%s"' % key,
		   '',
		   str(value),
		   ])
	# Now add the file itself
	if content is None:
		if file is None:
			raise ValueError('need file or content argument')
		if hasattr(file, 'read'):
			content = file.read()
		else:
			name = os.path.basename(file)
			f = open(file, 'rb')
			content = f.read()
			f.close()

	#print 'type content: %s, len content: %s' % (type(content), len(content))

	if name is None:
		ext = guess_image_ext(content[:32])
		name = 'data.{}'.format(ext)

	if content_type is None:
		content_type = guess_mimetype(name)

	body.extend(
	  ['--' + BOUNDARY,
	   str('Content-Disposition: form-data; name="file"; filename="%s"' % name),
	   # The upload server determines the mime-type, no need to set it.
	   str('Content-Type: %s' % content_type),
	   '',
	   content,
	   ])
	# Finalize the form body
	body.extend(['--' + BOUNDARY + '--', ''])
	return 'multipart/form-data; boundary=%s' % BOUNDARY, CRLF.join(body)


sig_gif = b'GIF'
sig_jpg = b'\xff\xd8\xff'
#sig_png = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
sig_png = b"\211PNG\r\n\032\n"

def guess_image_ext(data):
	if data[:3] == sig_gif:
		return 'gif'
	elif data[:3] == sig_jpg:
		return 'jpg'
	elif data[:8] == sig_png:
		return 'png'
	else:
		return None

def guess_mimetype(fn, default="application/octet-stream"):
	"""Guess a mimetype from filename *fn*.

	>>> guess_mimetype("foo.txt")
	'text/plain'
	>>> guess_mimetype("foo")
	'application/octet-stream'
	"""
	import mimetypes
	if "." not in fn:
		return default
	bfn, ext = fn.lower().rsplit(".", 1)
	if ext == "jpg": ext = "jpeg"
	return mimetypes.guess_type(bfn + "." + ext)[0] or default

def mime_to_ext(mime):
	import mimetypes
	ext = mimetypes.guess_extension(mime)
	if ext == '.jpe':
		return '.jpg'
	return ext
