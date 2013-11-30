# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup
from setuptools import find_packages

version = '0.1'

install_requires = ['venusian', 'docopt']

if sys.version_info[:2] < (3, 4):
    install_requires.append('asyncio')


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='irc3',
    version=version,
    description="irc3 package",
    long_description=read('README.rst'),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='',
    author='Gael Pasgrimaud',
    author_email='gael@gawel.org',
    url='https://github.com/gawel/irc3/',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'nose', 'coverage'
        ],
    },
)
