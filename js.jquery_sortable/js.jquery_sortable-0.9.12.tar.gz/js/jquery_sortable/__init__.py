# -*- coding: utf-8 -*-

"""
Created on 2014-05-12
:author: Andreas Kaiser (disko)
"""

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library('jquery_sortable', 'resources')

jquery_sortable = Resource(
    library,
    'jquery-sortable.js',
    minified='jquery-sortable.min.js',
    depends=[jquery, ])
