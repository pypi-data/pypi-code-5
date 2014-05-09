#!/usr/bin/env python
"""
"""
import time
import select

from ..resource import SharedResource


class BasicDevice(object):
    """
    """

    DEFAULT_ENCODING = 'ascii'
    DEFAULT_RECV_COUNT = -1
    
    SEND_TERMINATION = '\n'
        
    def __init__(self, timeout=30.0):
        object.__init__(self)
        self._stdio = None
        
        self.timeout = timeout
        
    def send(self, message, encoding=DEFAULT_ENCODING):
        """
        """
        # TODO: store termination in bytes, then add to encoded message right before send.
        if not message.endswith(self.SEND_TERMINATION):
            message += self.SEND_TERMINATION
        if encoding:
            self.stdio.write(message.encode(encoding))
        else:
            self.stdio.write(message)
        
    def receive(self, count=DEFAULT_RECV_COUNT, encoding=DEFAULT_ENCODING):
        """
        """
        received = bytearray()
        start_time = time.time()
        while True:
            ready_read, ready_write, in_error = select.select([self.stdio], [], [], 0)
            if self.stdio in ready_read:
                chunk = self.stdio.read()
                received.extend(chunk)
                if len(received) >= count:
                    break
                else:
                    start_time = time.time()
            if (time.time() - start_time) > self.timeout:
                break
        
        if encoding:
            return received.decode(encoding=encoding)
        else:
            return bytes(received)
        
    @property
    def stdio(self):
        return self._stdio
        
    @stdio.setter
    def stdio(self, io):
        self._stdio = io


class Device(SharedResource, BasicDevice):
    """
    """
    def __init__(self, *args, uuid=None, name=None, make=None, model=None, version=None, **kwargs):
        SharedResource.__init__(self)
        BasicDevice.__init__(self, *args, **kwargs)
        self._uuid = uuid
        self.name = name
        self.make = make
        self.model = model
        self.version = version
