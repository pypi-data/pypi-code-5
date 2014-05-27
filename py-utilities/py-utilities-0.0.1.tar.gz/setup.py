#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import py_utilities

packages = [
    'py_utilities',
    'py_utilities.collections',
    'py_utilities.crypto',
    'py_utilities.dev',
    'py_utilities.excel',
    'py_utilities.fs',
    'py_utilities.http',
    'py_utilities.image',
    'py_utilities.math',
    'py_utilities.mixins',
    'py_utilities.patterns',
    'py_utilities.text',
    'py_utilities.time',
    'py_utilities.ui',
]

requires = ['pytz', 'importlib', 'scrypt', 'xlrd', 'ordereddict']
tests_require = ['flake8', 'mock', 'nose', 'nosexcover']

with open('README.rst') as f:
    readme = f.read()

with open('CHANGES') as f:
    changes = f.read()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Topic :: Utilities'
]

setup(
    name='py-utilities',
    version=py_utilities.__version__,
    description='Collection of python utilities',
    long_description=readme + '\n\n' + changes,
    author='Ryan Kanno',
    author_email='ryankanno@localkinegrinds.com',
    url="https://github.com/ryankanno/py-utilities",
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'py_utilities': 'py_utilities'},
    install_requires=requires,
    license='MIT',
    tests_require=tests_require,
    classifiers=classifiers,
)

# vim: filetype=python
