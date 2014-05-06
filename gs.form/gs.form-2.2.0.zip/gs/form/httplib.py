# -*- coding: utf-8 -*-
'''Import the correct HTTPConnection and HTTPSConnection classes from Python,
regardless of 2 or 3.'''
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
import sys
if (sys.version_info < (3, )):
    from httplib import HTTPSConnection, HTTPConnection
else:
    from http.client import HTTPSConnection, HTTPConnection  # lint:ok
