#!/usr/bin/env python
from setuptools import setup

setup(
    name='distutils-licenses',
    version='0.1.2',

    author='Daniel A. Koepke',
    author_email='dkoepke@gmail.com',
    license='MIT',

    description='adds a command to setup.py to list licenses of packages',
    long_description=open('README.txt').read(),

    url='http://github.com/dkoepke/distutils-licenses',
    packages=['distutils_licenses'],

    entry_points={
        'distutils.commands': [
            'licenses = distutils_licenses.command:LicenseCommand',
        ],
    }
)
