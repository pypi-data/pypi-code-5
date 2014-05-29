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

from ..defaultencoding import DefaultEncoding
from ..import channel


class Response(object):
    """
    """
    def __init__(self, device=None, io=None, encoding=DefaultEncoding(), receive_count=-1):
        object.__init__(self)
        self.device = device
        self.io = io
        self.encoding = encoding
        self.receive_count = receive_count
        
        self.__response = None
        
    @property
    def value(self):
        """The most recently retrieved response.
        """
        return self.__response
        
    def __call__(self):
        """Performs a device read, using the currently set io, and stores the value.
        """
        if isinstance(self.encoding, DefaultEncoding):
            with channel(self.device, self.io) as dev:
                self.__response = dev.receive(self.receive_count)
        else:
            with channel(self.device, self.io) as dev:
                self.__response = dev.receive(self.receive_count, encoding=self.encoding)
