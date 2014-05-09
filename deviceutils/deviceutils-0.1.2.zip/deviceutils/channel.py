#!/usr/bin/env python
"""
"""
import contextlib


@contextlib.contextmanager
def channel(device_instance, io_):
    """Attach a stateful device instance to a file-like IO, and open in this context.
    
    The file-like IO will be opened for communication, and then closed upon exit.
    """
    if io_.closed:
        io_.open()
    device_instance.stdio = io_
    yield device_instance
    io_.close()
    device_instance.stdio = None
