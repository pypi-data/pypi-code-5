#!/usr/bin/env python
"""
"""
import serial
import os

from ..resource import SharedResource
from .mixin import IORateLimiterMixin


class BasicSerialPort(serial.Serial):
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
    
    def __init__(self, port, timeout=30.0):
        """
        """
        serial.Serial.__init__(self, port=None)  # port=None prevents auto-open on init.
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
        """Avoid using this interface. Read SerialPort.closed instead.
        """
        return not self.isOpen()
        
    closed = property(is_closed)


class SerialPort(SharedResource, IORateLimiterMixin, BasicSerialPort):
    """
    """
    def __init__(self, *args, **kwargs):
        SharedResource.__init__(self)
        BasicSerialPort.__init__(self, *args, **kwargs)
