# -*- coding: utf-8 -*-
"""
format-sql

Copyright (c) 2014, Friedrich Paetzke (paetzke@fastmail.fm)
All rights reserved.

"""
from functools import wraps


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('%s: %s' % (func.__name__, args))
        return func(*args, **kwargs)

    return wrapper
