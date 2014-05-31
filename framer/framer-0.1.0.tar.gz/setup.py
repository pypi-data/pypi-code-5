#!/usr/bin/env python

import os
import sys

from setuptools import setup


def readreq(filename):
    result = []
    with open(filename) as f:
        for req in f:
            req = req.lstrip()
            if req.startswith('-e ') or req.startswith('http:'):
                idx = req.find('#egg=')
                if idx >= 0:
                    req = req[idx + 5:].partition('#')[0].strip()
                else:
                    pass
            else:
                req = req.partition('#')[0].strip()
            if not req:
                continue
            result.append(req)
    return result


def readfile(filename):
    with open(filename) as f:
        return f.read()


# Read in the requirements.txt file first
install_requires = readreq('requirements.txt')

# Determine what package we need to add to get asyncio
if sys.version_info >= (3, 4):
    pass
elif sys.version_info >= (3, 3):
    install_requires.append('asyncio')
elif sys.version_info >= (2, 6):
    install_requires.append('trollius')
else:
    sys.exit("No support for asyncio available in this version of Python")


setup(
    name='framer',
    version='0.1.0',
    author='Kevin L. Mitchell',
    author_email='klmitch@mit.edu',
    url='https://github.com/klmitch/framer',
    description="Network Framer Library",
    long_description=readfile('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=['framer'],
    install_requires=install_requires,
    tests_require=readreq('test-requirements.txt'),
)
