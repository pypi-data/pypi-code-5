# -*- coding: utf-8 -*-
from __future__ import absolute_import
import ast
from os import environ

DEFAULT_ENV_PREFIX = 'FLASK_'


class EnvConfig(object):
    """Configure Flask from environment variables."""

    def __init__(self, app=None, prefix=DEFAULT_ENV_PREFIX):
        self.app = app
        if app is not None:
            self.init_app(app, prefix)

    def init_app(self, app, prefix=DEFAULT_ENV_PREFIX):
        for key, value in environ.iteritems():
            if key.startswith(prefix):
                key = key[len(prefix):]
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass
                app.config[key] = value

