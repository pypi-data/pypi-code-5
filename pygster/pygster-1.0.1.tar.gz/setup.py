#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for the Pygster.

Source:: https://github.com/OnBeep/pygster
"""

__title__ = 'pygster'
__version__ = '1.0.1'
__build__ = '0x010001'
__author__ = 'Greg Albrecht  <gba@onbeep.com>'
__copyright__ = 'Copyright 2014 OnBeep, Inc. and Contributors'
__license__ = 'GNU General Public License, Version 3'


import os
import sys


try:
    from setuptools import setup
except ImportError:
    # pylint: disable=F0401,E0611
    from distutils.core import setup


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == 'publish':
        os.system('python setup.py sdist upload')
        sys.exit()


publish()


setup(
    name=__title__,
    version=__version__,
    description='Pygster',
    long_description=open('README.rst').read(),
    author='Greg Albrecht',
    author_email='gba@onbeep.com',
    license=open('LICENSE').read(),
    url='https://github.com/OnBeep/pygster',
    setup_requires=['nose'],
    tests_require=['coverage', 'nose'],
    install_requires=['pygtail==0.3.0'],
    package_dir={'pygster': 'pygster'},
    packages=['pygster', 'pygster/parsers'],
    scripts=['bin/pygster'],
    zip_safe=False
)
