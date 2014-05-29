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

import socket
import io
import multiprocessing

from .mixin import IORateLimiterMixin
from deviceutils.error import IOTimeoutError


def receive_proc(return_queue, sock, count):
    try:
        return_queue.put_nowait(sock.recv(count))
    except Exception as e:
        return_queue.put_nowait(e)


# TODO: multiprocess approach will pickle io objects... The goal is to use a Manager instead in final implementation.
class BasicTcpSocket(io.IOBase):
    """
    """
    def __init__(self, host, port, timeout=None, buffer_size=4096):
        super().__init__()
        self._socket = None
        self.host = host
        self.port = port
        self.timeout = timeout
        self._closed = True
        self._just_marshaled = False
        self.read_buffer_size = buffer_size
    
    def close(self):
        if self._just_marshaled:
            self._unmarshal

        if self._socket is not None:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        # re-instantiate so that the socket can be used again.
        self._socket = None
        self._closed = True

    @property
    def closed(self):
        return self._closed

    def fileno(self):
        if self.closed:
            raise ValueError('I/O operation on closed io.')
        return self._socket.fileno(self)
        
    def flush(self):
        if self.closed:
            raise ValueError('I/O operation on closed io.')
    
    def readable(self):
        return not self._closed
        
    def read(self, size=None):
        if self.closed:
            raise ValueError('I/O operation on closed io.')

        if self._just_marshaled:
            self._unmarshal

        if not size or size < 0:
            size = self.read_buffer_size

        receive_queue = multiprocessing.Queue()
        p_reader = multiprocessing.Process(target=receive_proc, args=(receive_queue, self._socket, size))
        p_reader.start()
        p_reader.join(timeout=self.timeout)
        if p_reader.is_alive():
            # the receive has timed out!
            p_reader.terminate()
            p_reader.join()
            raise IOTimeoutError('i/o timed out during read.')
        received = receive_queue.get_nowait()
        if isinstance(received, Exception):
            raise received
        return bytes(received)

    def writable(self):
        return not self._closed
        
    def write(self, b):
        if self.closed:
            raise ValueError('I/O operation on closed io.')

        if self._just_marshaled:
            self._unmarshal

        return self._socket.send(b)
        
    def open(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))
        self._closed = False

    def _marshal(self):
        self._just_marshaled = True

    def _unmarshal(self):
        self._just_marshaled = False

    #def __getstate__(self):
        # handle a pickle while opened!
        #state = super().__getstate__()
        #if not self.closed:
            #state['_socket'] = None
        #return state


    #def __setstate__(self, state):
        # reinstate self, and handle an unpickle of an object that was pickled while open!
        #pass
        

class TcpSocket(IORateLimiterMixin, BasicTcpSocket):
    """
    """
    def __init__(self, *args, **kwargs):
        BasicTcpSocket.__init__(self, *args, **kwargs)
