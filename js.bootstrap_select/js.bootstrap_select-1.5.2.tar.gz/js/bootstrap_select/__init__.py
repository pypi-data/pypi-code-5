# -*- coding: utf-8 -*-
"""Fanstatic packaging of bootstrap-select.js."""

from fanstatic import Group, Library, Resource
from js.bootstrap import bootstrap_css, bootstrap_js

library = Library('bootstrap_select', 'resources')

bootstrap_select_css = Resource(
    library, 'bootstrap-select.css',
    minified='bootstrap-select.min.css',
    depends=[
        bootstrap_css,
    ],
)

bootstrap_select_js = Resource(
    library, 'bootstrap-select.js',
    minified='bootstrap-select.min.js',
    depends=[
        bootstrap_js,
    ],
)

bootstrap_select = Group([bootstrap_select_js, bootstrap_select_css])
