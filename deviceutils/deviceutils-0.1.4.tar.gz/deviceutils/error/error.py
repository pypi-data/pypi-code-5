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

import io


class DeviceError(Exception):
    """
    """
    def __init__(self, message='', uuid=None, name=None, make=None, model=None, version=None):
        self._uuid = uuid
        self.name = name
        self.make = make
        self.model = model
        self.version = version
        super().__init__(message)


class DeviceTimeoutError(DeviceError):
    pass


class DeviceIOError(IOError):
    pass


class IOTimeoutError(DeviceIOError):
    pass


class ProtocolError(Exception):
    """
    """
    pass
