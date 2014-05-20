#!/usr/bin/env python

#
# This file is part of SpectralToolbox.
#
# SpectralToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectralToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with SpectralToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import os.path
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

local_path = os.path.split(os.path.realpath(__file__))[0]
version_file = open(os.path.join(local_path, 'VERSION'))
version = version_file.read().strip()

setup(name = "SpectralToolbox",
      version = version,
      packages=find_packages(),
      include_package_data=True,
      scripts=[],
      url="http://www2.compute.dtu.dk/~dabi/index.php?slab=dtu-uq",
      author = "Daniele Bigoni",
      author_email = "dabi@dtu.dk",
      license="COPYING.LESSER",
      long_description=open("README.txt").read(),
      install_requires=['numpy',
                        'scipy',
                        'Sphinx',
                        'progressbar',
                        'orthpol >= 0.1.2']
      )
