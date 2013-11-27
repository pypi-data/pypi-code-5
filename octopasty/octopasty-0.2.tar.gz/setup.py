#!/usr/bin/python
# -*- coding: utf-8 -*-

# Octopasty is an Asterisk AMI proxy

# Copyright (C) 2011  Jean Schurger <jean@schurger.org>

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

from setuptools import setup
from octopasty import __version__

entry_points = '''\
[console_scripts]
opasty = octopasty.opasty:main
pasty = octopasty.pasty:main
'''

setup(name='octopasty',
      version=__version__,
      description="Octopasty Asterisk AMI proxy",
      author="Jean Schurger",
      author_email='jean@schurger.org',
      url='http://ubity.com',
      packages=['octopasty'],
      install_requires=['gevent', 'pyyaml'],
      license='GPLv3',
      package_data={'octopasty': ['../docs/*']},
      entry_points=entry_points)
