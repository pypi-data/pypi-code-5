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

from datetime import datetime, timedelta
from time import sleep


class IORateLimiterMixin(object):
    """Provide the ability to limit the number of sends and receives per second.
    
    This can be useful for preventing IO flooding at the software level.
    
    NOTE: This should be mixed-in with ``IOBase`` compatible parent.
    """
    __time_of_last_io = None  # default, DO NOT CHANGE.
    __io_wait_time = 0.0  # default, DO NOT CHANGE.
    
    @property
    def io_min_delta(self):
        """The minimum time which must elapse between each send/receive operation (seconds).
        
        Floating point numbers (or equivalent) can be used to set subsecond 
        intervals.
        """
        return self.__io_wait_time
    
    @io_min_delta.setter
    def io_min_delta(self, value):
        self.__io_wait_time = value
    
    def __io_wait(self):
        """Wait until the minimum time between I/O operations has passed.
        
        :return bool: Whether a wait was performed during this call.
        """
        if self.__io_wait_time > 0:
            if self.__time_of_last_io:
                # have we waited long enough before sending again?
                elapsed = datetime.utcnow() - self.__time_of_last_io
                try:                
                    self.log.debug(
                        "Elapsed time from previous I/O: {0} s".format(elapsed.total_seconds()))
                except AttributeError:
                    pass
                min_wait = timedelta(seconds=float(self.__io_wait_time))
                remaining = (min_wait - elapsed).total_seconds()
                if remaining > 0:
                    try:
                        self.log.debug(
                            "Pausing for {0} seconds".format(remaining))
                    except AttributeError:
                        pass
                    sleep(remaining)
                    return True  # did wait
        return False  # did not wait
    
    def write(self, *args, **kwargs):
        self.__io_wait()
        self.__time_of_last_io = datetime.utcnow()
        return super().write(*args, **kwargs)
    
    def read(self, *args, **kwargs):
        self.__io_wait()
        self.__time_of_last_io = datetime.utcnow()
        return super().read(*args, **kwargs)

