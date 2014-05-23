from distutils.core import setup
setup(
  name = 'rescale',
  packages = ['rescale'],
  version = '0.2',
  description = 'A simple tool to resize and crop an image',
  author = 'evuez',
  author_email = 'helloevuez@gmail.com',
  url = 'https://github.com/evuez/python-rescale',
  download_url = 'https://github.com/evuez/python-rescale/tarball/0.2',
  keywords = ['image', 'scale', 'crop', 'resize'],
  classifiers = [],
  install_requires=['Pillow'],
)
