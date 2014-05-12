#!/usr/bin/env python
# coding=utf-8
import sys
from copy import copy

from setuptools import setup, find_packages


# Defaults for py2app / cx_Freeze
default_build_options=dict(
    packages=[
        'matplotlib',
        ],
    includes=[
        ],
    excludes=[
        ],
    )



setup(

    name='mplstyler',
    version="0.1",
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/mfitzp/mplstyler',
    download_url='https://github.com/mfitzp/mplstyler/zipball/master',
    description='An API for assigning consistent marker styles to plots. Assign colours, markers, line-styles to labels and re-use on subsequent plots.',
    long_description='mplstyler is a simple API for assigning consistent marker styles to plots. \
    Assign colours, markers, line-styles to labels and re-use on subsequent plots. Supports auto-assignment, manual assignment and pattern-matching.',

    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '': ['*.txt', '*.rst', '*.md'],
    },
    exclude_package_data = { '': ['README.txt'] },

    entry_points = {},

    install_requires = [
            'matplotlib>=1.0.0',
            ],

    keywords='bioinformatics research analysis science',
    license='GPL',
    classifiers=['Development Status :: 4 - Beta',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Education',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
              ],

    options={},
    )
