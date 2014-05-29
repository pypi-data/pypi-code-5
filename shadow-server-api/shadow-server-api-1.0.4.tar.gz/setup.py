#!/usr/bin/env python
import os
import sys

import shadow_server_api

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

with open('doc/README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()

setup(name='shadow-server-api'
        ,version=shadow_server_api.__version__
        ,description='Shadow Server - Binary Whitelist and MD5/SHA1 AV Service API'
        ,long_description=readme + '\n\n' + history
        ,url='https://github.com/blacktop/team-cymru-api'
        ,author='blacktop'
        ,author_email='dev@blacktop.io'
        ,license=shadow_server_api.__license__
        ,test_suite="tests"
        ,packages=['shadow_server_api']
        ,package_dir={'shadow_server_api': 'shadow_server_api'}
        ,install_requires=["requests >= 2.2.1"])
