#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import profiler

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = profiler.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='profile-middleware',
    version=version,
    description="""Profiler for django views""",
    long_description=readme + '\n\n' + history,
    author='Vaibhav Mishra',
    author_email='vinu76jsr@gmail.com',
    url='https://github.com/vinu76jsr/django_profiler',
    packages=[
        'profiler',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='profiler',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)