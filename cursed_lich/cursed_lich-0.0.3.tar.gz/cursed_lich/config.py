#!/usr/bin/env python

import os
import shutil

CONFIGS = {}

# Load the default server config from user's home
DEFAULT_CONFIG_DIR = os.path.join(os.getenv('HOME'), '.cursed_lich')
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, 'server_config.py')
SERVER_BASIC_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 'default_server_config.py')

def install_basic_config(path=DEFAULT_CONFIG_PATH):
    ''' Install the default config '''
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    shutil.copy(SERVER_BASIC_CONFIG_PATH, path)

def exec_config(path=DEFAULT_CONFIG_PATH):
    ''' Executes a config as Python code at a path '''
    d = {}
    if not os.path.isfile(path):
        raise ValueError('No server config at %s' % path)
    execfile(path, d)
    CONFIGS[d['SERVER_CONFIG'].SERVER_NAME] = d['SERVER_CONFIG']
    return d['SERVER_CONFIG']

def load_config(name=None):
    ''' Loads the default config, or the one specified.
    If a path is supplied, it executes it first.
    '''
    if name is None:
        configs = CONFIGS.items()
        if len(configs) > 1:
            raise ValueError('Ambiguous config to use. '
            'Multiple have been loaded.')
        elif len(configs) == 0:
            raise ValueError('No configs have been loaded.')
        return configs[0][1]
    else:
        # Either give back the one by name, or load name as the path.
        # If there's an exception, this means that you need to exec_config
        # and get it by SERVER_NAME.
        return CONFIGS.get(name, exec_config(path=name))
    
