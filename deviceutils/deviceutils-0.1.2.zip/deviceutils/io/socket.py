#!/usr/bin/env python
"""
"""
import socket

from ..resource import SharedResource
from .mixin import IORateLimiterMixin


class BasicTcpSocket(socket.socket):
    """
    """    
    
    def __init__(self, host, port, timeout=30.0, buffer_size=4096):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.settimeout(timeout)
        self.closed = True
        
        self.buffer_size = buffer_size
        
    @property
    def timeout(self):
        return self.gettimeout()
        
    @timeout.setter
    def timeout(self, value):
        self.settimeout(value)
    
    def close(self):
        self.shutdown(socket.SHUT_RDWR)
        socket.socket.close(self)
        # re-init so that the socket can be used again.
        BasicTcpSocket.__init__(self, self.host, self.port, timeout=self.timeout,
                                buffer_size=self.buffer_size)
        self.closed = True
        
    def fileno(self):
        return socket.socket.fileno(self)
        
    def flush(self):
        return self.makefile().flush()
    
    def readable(self):
        return not self.closed
        
    def read(self, size=-1):
        try:
            if not size or size < 0:
                return self.recv(self.buffer_size)
            else:
                return self.recv(size)
        except socket.timeout:
            return bytes([])
        except:
            raise
        
    def writable(self):
        return not self.closed
        
    def write(self, b):
        return self.send(b)
        
    def open(self):
        self.connect((self.host, self.port))
        self.closed = False
        

class TcpSocket(SharedResource, IORateLimiterMixin, BasicTcpSocket):
    """
    """
    def __init__(self, *args, **kwargs):
        SharedResource.__init__(self)
        BasicTcpSocket.__init__(self, *args, **kwargs)
