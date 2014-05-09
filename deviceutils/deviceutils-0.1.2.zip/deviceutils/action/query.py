#!/usr/bin/env python
"""
"""
from ..defaultencoding import DefaultEncoding
from ..channel import channel


class Query(object):
    """More than just a simple aggregate of a Command and a Response.
    
    Executes a command, attempts to retrieve an IMMEDIATE response, all without
    releasing the resource locks.
    """
    def __init__(self, message, device=None, io=None, 
                 send_encoding=DefaultEncoding(),
                 receive_encoding=DefaultEncoding(),
                 receive_count=-1):
        object.__init__(self)
        self.message = message
        self.device = device
        self.io = io
        self.send_encoding = send_encoding
        self.receive_encoding = receive_encoding
        self.receive_count = receive_count
        
        self.__response = None
        
    @property
    def value(self):
        """The most recently retrieved response.
        """
        return self.__response
        
    def __call__(self, *args, **kwargs):
        """Sends the command, fetches a response, stores and returns that response.
        
        Any arguments and/or keyword arguments will be passed to ``format``,
        which is called on the command message before sending.
        """
        self.io.lock.acquire()
        try:
            self.device.lock.acquire()
            
            try:
                if isinstance(self.send_encoding, DefaultEncoding):
                    with channel(self.device, self.io) as dev:
                        dev.send(
                            self.message.format(*args, **kwargs))
                        self.__response = dev.receive(count=self.receive_count)
                else:
                    with channel(self.device, self.io) as dev:
                        dev.send(
                            self.message.format(*args, **kwargs), encoding=self.send_encoding)
                        self.__response = dev.receive(count=self.receive_count, encoding=self.receive_encoding)
            
            except:
                raise
            finally:
                self.device.lock.release()
        
        except:
            raise
        finally:
            self.io.lock.release()
        
        return self.value

