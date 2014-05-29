#!/usr/bin/env python
"""
"""
# Python 2.6 and newer support
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (
                bytes, dict, int, list, object, range, str,
                ascii, chr, hex, input, next, oct, open,
                pow, round, super,
                filter, map, zip)
try:
    unicode()
except NameError:
    unicode = str

import sys
__python_version__ = dict()
try:
    __python_version__['major'] = sys.version_info.major
except AttributeError:
    __python_version__['major'] = sys.version_info[0]
try:
    __python_version__['minor'] = sys.version_info.minor
except AttributeError:
    __python_version__['minor'] = sys.version_info[1]

import contextlib


@contextlib.contextmanager
def channel(device_instance, io_):
    """Attach a stateful device instance to a file-like IO, and open in this context.
    
    The file-like IO will be opened for communication, and then closed upon exit.
    """
    if io_.closed:
        io_.open()
    device_instance.stdio = io_
    yield device_instance
    io_.close()
    device_instance.stdio = None
