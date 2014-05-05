#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='advanced_jabberclient',
    version='1.0.0',
    description='Advanced jabber client with ping timeouts',
    license='BSD',
    url='https://github.com/ruscoder/advanced_jabberclient',
    author='Vadim',
    author_email='Vadim <rusmiligamer@gmail.com>',
    py_modules=['advanced_jabberclient.jabberclient'],
    install_requires=[
            'Twisted>=12.0.0',
            ],
    keywords='twisted module jabber client ping timeout',
)
