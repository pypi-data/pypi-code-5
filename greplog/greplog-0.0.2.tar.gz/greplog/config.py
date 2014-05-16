#!/usr/bin/env python

"""
greplog.config
~~~~~~~~~~~~~~

Parse and utilize configuration files, in $HOME

"""

import os

CONFIG_DIR = os.path.join(os.getenv('HOME'), '.greplog')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'default.py')
SERVER_PATH = os.path.join(CONFIG_DIR, 'servers.py')

class Config(object):
    """
    Stores the global and user configs, and loads it into the namespace.
    """

    CONFIG_D = {}
    if os.path.exists(CONFIG_PATH):
        execfile(CONFIG_PATH, CONFIG_D)
    if os.path.exists(SERVER_PATH):
        execfile(SERVER_PATH, CONFIG_D)

    def __init__(self, *args):
        self.config_d = {}
        for config_path in args:
            if os.path.exists(config_path):
                execfile(config_path, self.config_d)

    def __getattr__(self, attr):
        if attr in self.config_d:
            return self.config_d[attr]
        if attr in Config.CONFIG_D:
            return Config.CONFIG_D[attr]
        raise AttributeError('Requested: %s\nContains: %s' % (
            attr,
            Config.CONFIG_D.items() + self.config_d.items(),
        ))

