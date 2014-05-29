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

import telnetlib
import socket

from ..resource import SharedResource
from .mixin import IORateLimiterMixin


class BasicTelnetPortal(telnetlib.Telnet):
    """
    """    
    
    def __init__(self, host, port, *args, **kwargs):
        # chose to do the following for backward compatibility with Python 2.x
        timeout = kwargs.pop('timeout', 30.0)

        telnetlib.Telnet.__init__(self, *args, **kwargs)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.closed = True
    
    def close(self):
        telnetlib.Telnet.close(self)
        self.closed = True
    
    def flush(self):
        return self.get_socket.makefile().flush()
    
    def readable(self):
        return not self.closed
        
    def read(self, size=-1):
        try:
            return self.read_very_eager()
        except socket.timeout:
            return bytes([])
        except:
            raise
        
    def writable(self):
        return not self.closed
        
    def write(self, b):
        return telnetlib.Telnet.write(self, b)
        
    def open(self):
        telnetlib.Telnet.open(self, self.host, port=self.port)
        self.closed = False
        

class TelnetPortal(SharedResource, IORateLimiterMixin, BasicTelnetPortal):
    """
    """
    def __init__(self, *args, **kwargs):
        SharedResource.__init__(self)
        BasicTelnetPortal.__init__(self, *args, **kwargs)

