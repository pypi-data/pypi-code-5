#!/usr/bin/env python
# -*- coding: utf-8 -*-

__title__ = 'bit9-api'
__version__ = '1.0.8'
__author__ = 'Josh Maine'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (C) 2014 Josh "blacktop" Maine'

try:
    import requests
except ImportError:
    pass

from .api import Bit9Api, vaildate_input, BadCreds, BadDataFormat
