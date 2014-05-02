#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2014 Adam Dybbroe

# Author(s):

#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


try:
    with open("./README", "r") as fd:
        long_description = fd.read()
except IOError:
    long_description = ""


from setuptools import setup
import imp

version = imp.load_source('pypps_reader.version', 'pypps_reader/version.py')

setup(name='pypps_reader',
      version="v0.1.1",
      description='NWCSAF pps data reader',
      author='Adam Dybbroe',
      author_email='adam.dybbroe@smhi.se',
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: GNU General Public License v3 " +
                   "or later (GPLv3+)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Scientific/Engineering"],
      url = "https://github.com/adybbroe/pypps_reader",
      download_url = "https://github.com/adybbroe/pypps_reader/tarball/0.1.1 #egg=pypps_reader-v0.1.1",
      long_description=long_description,
      license='GPLv3',

      packages = ['pypps_reader'],

      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires=['docutils>=0.3', 
                        'numpy', 'h5py'],
      extras_require = {'geolocation layout for pyresample': ['pyresample'],
                        },
      scripts = [],      
      data_files=[('etc', ['etc/pps_reader.cfg'])],
      test_suite="nose.collector",
      tests_require=[],

      zip_safe = False
      )
