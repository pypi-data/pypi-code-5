#!/usr/bin/env python

#
# This file is part of TensorToolbox.
#
# TensorToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TensorToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TensorToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import TensorToolbox
from os.path import exists
import sys, getopt
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if "--without-mpi4py" in sys.argv:
    deps = ['numpy','scipy','Sphinx','prettytable','SpectralToolbox >= 0.1']
    idx = sys.argv.index('--without-mpi4py')
    del sys.argv[idx]
else:
    deps = ['numpy','scipy','Sphinx','prettytable','SpectralToolbox >= 0.1','mpi4py']
    

# deps = ['numpy','scipy','Sphinx','prettytable','SpectralToolbox >= 0.1']
setup(name = "TensorToolbox",
      version = TensorToolbox.__version__,
      packages=find_packages(),
      include_package_data=True,
      scripts=[],
      url="http://www2.compute.dtu.dk/~dabi/index.php?slab=dtu-uq",
      author = "Daniele Bigoni",
      author_email = "dabi@dtu.dk",
      license="COPYING.LESSER",
      long_description=open("README.txt").read(),
      zip_safe = False,         # I need this for MPI purposes
      install_requires=deps
      )
