#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-xmlrpc',
    version = '2.0',
    description = 'An extensible XML-RPC provider',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'https://github.com/iamsteadman/bambu-xmlrpc',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = ['Django>=1.4'],
    packages = ['bambu_xmlrpc'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)