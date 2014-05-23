"""
Setup functions for Pepper API work




"""
# distutils: language = c++

#-----------------------------------------------------------------------------
# Copyright (c) 2013, Matthew J. Turk
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

# These functions insert some dummies into the various Python libraries.

import socket
import sys
import glob

try:
    socket.gethostname()
except:
    print "Replacing gethostname()"
    socket.gethostname = lambda: 'localhost'

from .ppapi_wrapper import NaClInstance
nacl_instance = NaClInstance()
nacl_instance.pylab()

def fix_missing_eggs():
    for fn in glob.glob("/lib/python2.7/site-packages/*.egg"):
        if fn not in sys.path:
            print "Appending %s to path" % fn
            sys.path.append(fn)

fix_missing_eggs()

__all__ = ['nacl_instance']
