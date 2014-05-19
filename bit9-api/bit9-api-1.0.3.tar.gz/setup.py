#!/usr/bin/env python
import os
import sys

import bit9_api

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('doc/README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(name='bit9-api'
        ,version=bit9_api.__version__
        ,description='Bit9 API for their Cyber Forensics Service'
        ,long_description=readme + '\n\n' + history
        ,url='https://github.com/blacktop/bit9-api'
        ,author='blacktop'
        ,author_email='dev@blacktop.io'
        ,license=bit9_api.__license__
        ,test_suite="tests"
        ,packages=['bit9_api']
        ,package_dir={'bit9_api': 'bit9_api'}
        ,install_requires=["requests >= 2.2.1"])
