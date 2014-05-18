#!/usr/bin/env python
from setuptools import setup
from os import path

setup(
    name = 'bambu-signup',
    version = '2.0',
    description = 'A fluid signup method for free web apps',
    author = 'Steadman',
    author_email = 'mark@steadman.io',
    url = 'http://pypi.python.org/pypi/bambu-formatrules',
    long_description = open(path.join(path.dirname(__file__), 'README')).read(),
    install_requires = [
        'Django>=1.4',
        'bambu-mail'
    ],
    packages = [
        'bambu_signup',
        'bambu_signup.migrations',
        'bambu_signup.views'
    ],
    package_data = {
        'bambu_signup': [
            'templates/signup/*.html',
            'templates/signup/mail/*.txt'
        ]
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ]
)