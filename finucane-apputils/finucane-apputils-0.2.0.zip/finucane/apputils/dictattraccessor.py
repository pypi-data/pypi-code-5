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


class DictAttrAccessor(object):
    def __init__(self, dict_=None):
        if isinstance(dict_, dict):
            self._dict = dict_
        else:
            raise TypeError('Expected ``dict``')
        # we must do this here, otherwise we can't set the attributes above.
        self.__setattr__ = self.__setitem__

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    __getattr__ = __getitem__
