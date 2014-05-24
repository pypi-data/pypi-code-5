#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
	name = 'bambu-api',
	version = '2.0.1',
	description = 'Quickly expose your models to a JSON or XML API, authenticated via HTTP or OAuth.',
	author = 'Steadman',
	author_email = 'mark@steadman.io',
	url = 'https://github.com/iamsteadman/bambu-api',
	long_description = open(path.join(path.dirname(__file__), 'README')).read(),
	install_requires = [
		'Django>=1.4',
		'oauth',
		'oauth2'
	],
	packages = [
		'bambu_api',
		'bambu_api.auth',
		'bambu_api.migrations',
		'bambu_api.templatetags',
		'bambu_api.xml'
	],
	package_data = {
		'bambu_api': [
			'templates/api/*.html',
			'templates/api/apps/*.html',
			'templates/api/auth/*.html',
			'templates/api/auth/oauth/*.html',
			'templates/api/doc/*.html'
		]
	},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django'
	]
)
