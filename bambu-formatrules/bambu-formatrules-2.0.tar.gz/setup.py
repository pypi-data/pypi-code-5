#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-formatrules',
    version = '2.0',
    description = 'Syntactical sugar ontop of Markdown for adding extra formatting, expressed in a human-readable way.',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'http://pypi.python.org/pypi/bambu-formatrules',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = [
        'Django>=1.4',
        'markdown'
    ],
    packages = [
        'bambu_formatrules',
        'bambu_formatrules.formatters',
        'bambu_formatrules.templatetags'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)