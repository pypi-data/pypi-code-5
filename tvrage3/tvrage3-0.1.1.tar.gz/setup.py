#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='tvrage3',
    version='0.1.1',
    description='Python3 client for accessing tv show information from www.tvrage.com',
    long_description=readme + '\n\n' + history,
    author='Kalle Lindqvist',
    author_email='kalle.lindqvist@mykolab.com',
    url='https://github.com/kalind/tvrage3',
    packages=[
        'tvrage3',
    ],
    package_dir={'tvrage3':
                 'tvrage3'},
    include_package_data=True,
    install_requires=['xmltodict'],
    license="BSD",
    zip_safe=False,
    keywords='tvrage, tv, show',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ],
    test_suite='tests',
)
