#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-mapping',
    version = '2.0',
    description = 'A pluggable, provider-based system for rendering maps',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'https://github.com/iamsteadman/bambu-mapping',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = [
        'Django>=1.4',
        'django-bower'
    ],
    packages = [
        'bambu_mapping',
        'bambu_mapping.providers',
        'bambu_mapping.templatetags',
    ],
    package_data = {
        'bambu_mapping': [
            'templates/mapping/*.js'
        ]
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)
