#!/usr/bin/env python
"""
"""


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
