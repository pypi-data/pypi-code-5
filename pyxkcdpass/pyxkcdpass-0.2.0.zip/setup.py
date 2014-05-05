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
    name='pyxkcdpass',
    version='0.2.0',
    description='This script provides a simple way to generate secure and human readable passwords, based on XKCD #936',
    long_description=readme + '\n\n' + history,
    author='Henrique Pereira',
    author_email='ikkibr@gmail.com',
    url='https://github.com/ikkebr/pyxkcdpass',
    py_modules = ['pyxkcdpass'],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='pyxkcdpass',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    entry_points={'console_scripts': ['pyxkcdpass = pyxkcdpass:main']}
)
