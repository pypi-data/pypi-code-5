#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dbaas_flipper',
    version='0.0.1',
    description='Flipper integration 4 DBaaS',
    long_description=readme + '\n\n' + history,
    author='Felippe da Motta Raposo',
    author_email='raposo.felippe@gmail.com',
    url='https://github.com/felippemr'
        '/dbaas-flipper',
    packages=[
        'dbaas_flipper',
    ],
    package_dir={'dbaas_flipper':
                 'dbaas_flipper'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='dbaas_flipper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)