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


class Command(object):
    """
    """
    def __init__(self, message, device=None, io=None, encoding=DefaultEncoding()):
        object.__init__(self)
        self.message = message
        self.device = device
        self.io = io
        self.encoding = encoding
    
    def __call__(self, *args, **kwargs):
        """Performs the command. The ``message`` is sent to the device using io.
        
        Any arguments and/or keyword arguments will be passed to ``format``,
        which is called on the command message before sending.
        """
        if isinstance(self.encoding, DefaultEncoding):
            with channel(self.device, self.io) as dev:
                dev.send(
                    self.message.format(*args, **kwargs))
        else:
            with channel(self.device, self.io) as dev:
                dev.send(
                    self.message.format(*args, **kwargs), encoding=self.encoding)
