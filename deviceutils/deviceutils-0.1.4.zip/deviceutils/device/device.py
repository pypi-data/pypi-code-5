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

import time
import multiprocessing
from collections import defaultdict

from ..error import DeviceTimeoutError
from ..dictattraccessor import DictAttrAccessor


def receive_proc(return_queue, io, count):
    # the return queue should never be empty after execution!
    try:
        return_queue.put_nowait(io.read(count))
    except Exception as e:
        return_queue.put_nowait(e)


class Device(object):
    """
    """
    DEFAULT_ENCODING = 'ascii'
    DEFAULT_RECV_COUNT = -1
    
    SEND_TERMINATION = '\n'
        
    def __init__(self, uuid=None, name=None, make=None, model=None, version=None, timeout=None):
        object.__init__(self)
        self._stdio = None
        self.timeout = timeout

        self._uuid = uuid
        self.name = name
        self.make = make
        self.model = model
        self.version = version

        self.state = DictAttrAccessor(dict_=defaultdict(type(None)))
        
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
        # TODO: multiprocess approach will pickle io objects... The goal is to use a Manager instead in final implementation.
        receive_queue = multiprocessing.Queue()
        t_reader = multiprocessing.Process(target=receive_proc, args=(receive_queue, self.stdio, count))
        t_reader.start()
        t_reader.join(timeout=self.timeout)
        if t_reader.is_alive():
            # the read timed out!
            t_reader.terminate()
            t_reader.join()
            raise DeviceTimeoutError(uuid=self._uuid,
                                     name=self.name,
                                     make=self.make,
                                     model=self.model,
                                     version=self.version,
                                     message='device timed out during receive.')

        received = receive_queue.get_nowait()
        if isinstance(received, Exception):
            raise received
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
