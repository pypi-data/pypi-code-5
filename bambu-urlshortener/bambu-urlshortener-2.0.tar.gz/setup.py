#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-urlshortener',
    version = '2.0',
    description = 'Shrink a URL using an internal or external shortening service',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'https://github.com/iamsteadman/bambu-urlshortener',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = [
        'Django>=1.4',
        'requests>=2.0'
    ],
    packages = [
        'bambu_urlshortener',
        'bambu_urlshortener.migrations',
        'bambu_urlshortener.providers'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)