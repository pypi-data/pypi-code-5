#!/usr/bin/env python
#
#	Copyright 2013-2014, Marten de Vries
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.

from setuptools import setup
import os

info = {}
with open(os.path.join("pouchdb", "info.py")) as f:
	exec(f.read(), info)

setup(
	name=info["name"],
	version=info["__version__"],
	description="A Python interface to PouchDB",
	long_description="""Python-PouchDB provides an interface to all the
goodness of the PouchDB JavaScript library (http://pouchdb.com/). It's
released under the Apache License v2 and it also offers a synchronous
API.

Uses QtWebKit internally, so either PySide, PyQt4 or PyQt5 is required.""",
	author=info["__author__"],
	author_email="marten@openteacher.org",
	url="http://python-pouchdb.marten-de-vries.nl/",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Apache Software License",
		"Operating System :: MacOS :: MacOS X",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: POSIX",
		"Programming Language :: JavaScript",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Topic :: Database",
		"Topic :: Software Development :: Libraries",
	],
	packages=["pouchdb"],
	package_data={
		"pouchdb": ["bundle.js"],
	},
	test_suite="pouchdb.tests",
	use_2to3=True,
)
