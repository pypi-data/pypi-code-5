#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = []

"""
with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()
"""

setup(
    name='pysift',
    version='0.0.2',
    description='SiftScience API.',
    author='Rhys Elsmore',
    author_email='me@rhys.io',
    url='http://github.com/rhyselsmore/pysift',
    packages=[
        'pysift',
    ],
    package_data={'': ['LICENSE']},
    package_dir={'pysift': 'pysift'},
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',

    ),
)
