#!/usr/bin/env python
import os
import sys

import shadowserver_api

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('doc/README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(name='shadow-server-api'
        ,version=shadowserver_api.__version__
        ,description='Shadow Server - Binary Whitelist and MD5/SHA1 AV Service API'
        ,long_description=readme + '\n\n' + history
        ,url='https://github.com/blacktop/team-cymru-api'
        ,author='blacktop'
        ,author_email='dev@blacktop.io'
        ,license=shadowserver_api.__license__
        ,test_suite="tests"
        ,packages=['shadowserver_api']
        ,package_dir={'shadowserver_api': 'shadowserver_api'}
        ,install_requires=["requests >= 2.2.1"])
