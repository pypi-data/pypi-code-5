from __future__ import print_function
from distutils.core import setup
import sys

# Detect Python that is not version 2 and try to use python2 if it is in PATH
try:
    major_version = sys.version_info.major
except AttributeError:
    major_version = sys.version_info[0]

if major_version != 2:
    print('Cannot continue. This package requires Python 2.7', file=sys.stderr)
    sys.exit(1)

setup(
    name='ImgurShare',
    version='0.1.0',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=[],
    license='GPLv3',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords='imgur api wrapper PyImgur cli',
    scripts=['bin/imgur-share'],
)
