# -*- coding: utf-8 -*-
"""
best-before

Copyright (c) 2014, Friedrich Paetzke (paetzke@fastmail.fm)
All rights reserved.

"""
from datetime import datetime
from functools import wraps

__version__ = '0.1.0'
__author__ = 'Friedrich Paetzke'
__license__ = 'BSD'
__copyright__ = 'Copyright 2014 Friedrich Paetzke'


class InedibleError(Exception):
    pass


class best_before:

    def __init__(self, date):
        if isinstance(date, str):
            self._date = datetime.strptime(date, '%Y-%m-%d')
        else:
            self._date = date

    def __call__(self, func):
        if self._date < datetime.now():
            raise InedibleError("Time's up.")

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
