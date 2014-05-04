#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    EweeStats
    ~~~~~~~~~
    
    :copyright: Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
    :license: GPL-3.0, see LICENSE for details
"""

import os
import sys
import imp

__version__ = '0.0-alpha.2'

#Check python version
if sys.version_info[:2] < (2, 7):
    raise ImportError('EweeStats requires Python version 2.7 or above')
    
try:
    imp.find_module('smbus')
    imp.find_module('ezodf2')
    imp.find_module('pyfirmata')
    imp.find_module('pygal')
except ImportError:
    print('EweeStats needs smbus-cffi, ezodf2, pyfirmata and pygal\n')
    print('Install it with :\n \teasy_install-2.7 <package-name>')
    sys.exit()
