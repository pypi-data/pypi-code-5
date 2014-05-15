# -*- coding: utf-8 -*-
"""Non-Magical Multiple Dispatch"""
# :copyright: (c) 2009 - 2012 Thom Neale and individual contributors,
#                 All rights reserved.
# :license:   BSD (3 Clause), see LICENSE for more details.

VERSION = (0, 0, 2)
__version__ = '.'.join(str(p) for p in VERSION[0:3]) + ''.join(VERSION[3:])
__author__ = 'Thom Neale'
__contact__ = 'twneale@gmail.com'
__homepage__ = 'http://github.com/twneale/nmmd'
__docformat__ = 'restructuredtext'


from nmmd.base import Dispatcher, DispatchError, TypeDispatcher
from nmmd.ext.regex import RegexDispatcher


__all__ = ['Dispatcher', 'DispatchError']
