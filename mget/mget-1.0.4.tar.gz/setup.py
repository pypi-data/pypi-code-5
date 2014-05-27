#!/usr/bin/env python3 

import os, warnings
from setuptools import setup, find_packages

files_spec = [('share/doc/mget', ['README.txt'])]
root = os.path.dirname(os.path.abspath(__file__))
data_files = []

for dirname, files in files_spec:
	resfiles = []
	for fn in files:
		if not os.path.exists(fn): warnings.warn('Skipping file %s.' % fn)
		else: resfiles.append(fn)
	data_files.append((dirname, resfiles))

params={'data_files': data_files,
	'entry_points': {'console_scripts': ['mget = Mget:main']}}
setup(
	name='mget',
	version='1.0.4',
	description='HTTP video downloader',
	long_description='Small command-line program to download videos from  mp4upload.com & video sharing site and other http urls.',
	author='Ramesh Mani Maran',
	author_email='r4v0n3@gmail.com',
	packages=find_packages(),
	classifiers=[
	"Programming Language :: Python",
	("Topic :: Software Development :: Libraries :: Python Modules"),
	],
	keywords='download mget http file',
	license='MIT',
	**params)

