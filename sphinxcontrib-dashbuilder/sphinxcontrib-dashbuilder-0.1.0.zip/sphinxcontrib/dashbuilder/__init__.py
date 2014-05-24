# -*- coding: utf-8 -*-
"""
    sphinxcontrib-dashbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx Dash builder.

    :copyright: Copyright 2014 by shimizukawa@gmail.com.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import

from .builder import DashBuilder


def setup(app):
    app.add_builder(DashBuilder)

    app.add_config_value('dash_name', None, 'env')
    app.add_config_value('dash_icon_file', None, 'env')
    app.add_config_value('dash_translator_class', None, 'env')
    #app.add_config_value('dash_add_to_docsets', False, 'env')
