#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup, find_packages

# Shortcut for publishing to Pypi
# Source: https://github.com/kennethreitz/tablib/blob/develop/setup.py
if sys.argv[-1] == 'publish':
  os.system('python setup.py sdist upload')
  sys.exit()

with open('README.md') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

setup(
  # Metadate for upload to Pypi
  name='chanjo-ccds',
  version='0.2',
  description='CCDS to Chanjo BED converter',
  long_description=readme,
  keywords='coverage sequencing clinical exome completeness diagnostics',
  platform='UNIX',
  author='Robin Andeer',
  author_email='robin.andeer@gmail.com',
  url='https://github.com/robinandeer/chanjo-ccds',
  download_url='https://github.com/robinandeer/chanjo-ccds',
  license=license,
  packages=find_packages(exclude=('tests', 'docs')),
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering :: Bio-Informatics'
  ],
  zip_safe=False,

  # Runtime dependencies
  install_requires = [
    'chanjo'
  ],

  # Testing dependencies
  tests_require = [
    'pytest'
  ]
)
