#!/usr/bin/env python
"""
"""
import telnetlib
import socket

from ..resource import SharedResource
from .mixin import IORateLimiterMixin


class BasicTelnetPortal(telnetlib.Telnet):
    """
    """    
    
    def __init__(self, host, port, *args, timeout=30.0, **kwargs):
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

