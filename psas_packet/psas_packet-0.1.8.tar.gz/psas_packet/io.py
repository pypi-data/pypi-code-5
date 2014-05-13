#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

def _is_string_like(obj):
    """
    Check whether obj behaves like a string.
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True


class BinFile(object):

    def __init__(self, fname):

        # Try and see if the passed in file is filename (string?) or an object that might act like a file
        if _is_string_like(fname):
            self.fh = open(fname, 'rb')
        else:
            self.fh = fname

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.fh.close()

    def read(self, byte=1500):
        print(self.fh.read(byte))
