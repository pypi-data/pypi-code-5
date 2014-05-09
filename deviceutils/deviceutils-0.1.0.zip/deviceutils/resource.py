#!/usr/bin/env python
"""
"""
import threading


class SharedResource(object):
    """Any resource that needs to be shared across threads. Provides mechanisms.
    """
    def __init__(self):
        object.__init__(self)
        self.__lock = threading.Lock()
        
    @property
    def lock(self):
        """The lock object for this shared resource instance.
        """
        return self.__lock

