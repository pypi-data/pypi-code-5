#!/usr/bin/env python
"""
"""
from ..defaultencoding import DefaultEncoding
from ..channel import channel


class Response(object):
    """
    """
    def __init__(self, device=None, io=None, encoding=DefaultEncoding(), receive_count=-1):
        object.__init__(self)
        self.device = device
        self.io = io
        self.encoding = encoding
        self.receive_count = receive_count
        
        self.__response = None
        
    @property
    def value(self):
        """The most recently retrieved response.
        """
        return self.__response
        
    def __call__(self):
        """Performs a device read, using the currently set io, and stores the value.
        """
        self.io.lock.acquire()
        try:
            self.device.lock.acquire()
            
            try:
                if isinstance(self.encoding, DefaultEncoding):
                    with channel(self.device, self.io) as dev:
                        self.__response = dev.receive(self.receive_count)
                else:
                    with channel(self.device, self.io) as dev:
                        self.__response = dev.receive(self.receive_count, encoding=self.encoding)
            
            except:
                raise
            finally:
                self.device.lock.release()
        
        except:
            raise
        finally:
            self.io.lock.release()
