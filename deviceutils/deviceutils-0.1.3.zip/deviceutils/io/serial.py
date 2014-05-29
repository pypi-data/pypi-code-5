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

import os
import io

import serial  # third-party

from .mixin import IORateLimiterMixin


class BasicSerialPort(io.IOBase):
    """A basic serial port file-like IO class.
    """
    @staticmethod
    def available_ports():
        """
        Returns a generator for all available serial ports
        """
        if os.name == 'nt':
            # windows
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    s.close()
                    yield 'COM' + str(i + 1)
                except serial.SerialException:
                    pass
        else:
            # unix
            for port in serial.list_ports.comports():
                yield port[0]    
    
    def __init__(self, port, timeout=None):
        """
        """
        super().__init__()
        self._serial = serial.Serial(self, port=None)  # port=None prevents auto-open on init.
        self.timeout = timeout
        self.port = port
    
    def open(self):
        """
        """
        if self.port is None:
            # let the serial library handle this edge case:
            serial.Serial.open(self)
        
        if not isinstance(self.port, int) and self.port not in SerialPort.available_ports():
            raise IOError("``{p}`` is not available!".format(p=self.port))
            
        serial.Serial.open(self)
    
    def is_closed(self):
        """Avoid using this interface. Read SerialPort._closed instead.
        """
        return not self.isOpen()
        
    closed = property(is_closed)


class SerialPort(IORateLimiterMixin, BasicSerialPort):
    """
    """
    def __init__(self, *args, **kwargs):
        BasicSerialPort.__init__(self, *args, **kwargs)
