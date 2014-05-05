#!/usr/bin/python

from setuptools import setup, find_packages

setup(
	name = "verparser",
	version = "0.2",
	packages = find_packages(),
	scripts = ["verparser.py"],
	
	author = "Roman Zhiharevich",
	author_email = "rzhiharevich@gmail.com",
	description = "Simple module for parsing version strings.",
	license = "BSD 3-Clause",
	keywords = "version versioning simple strings"
)
