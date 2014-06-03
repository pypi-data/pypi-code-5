#!/usr/bin/env python
import os
import logging
import random

# Leave version as is. 
__version__ = 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Edit these goodies for simple configurations
#
SERVER_NAME = 'midgaard'
SERVER_PORT = 9900
# ~/.cursed_lich
CONFIG_DIR = os.path.abspath(os.path.join(os.getenv('HOME'), '.cursed_lich'))
# ~/.cursed_lich/midgaard.log
LOG_PATH = os.path.join(CONFIG_DIR, '%s.log' % SERVER_NAME)
LOGGER_LEVEL = logging.INFO # or DEBUG, WARNING, ERROR, CRITICAL
# Prints to stdout
STDOUT_LEVEL = logging.INFO # or similar to above
# ~/.cursed_lich/midgaard.db
DB_PATH = os.path.join(CONFIG_DIR, '%s.db' % SERVER_NAME)    
ADMIN_USERNAME = 'admin'
USE_SSL = True
# Generate this keypair with `cursed_lich_server -g`
# ~/.cursed_lich/midgaard.key
SSL_KEY_PATH = os.path.join(CONFIG_DIR, '%s.key' % SERVER_NAME)
# ~/.cursed_lich/midgaard.crt
SSL_CERT_PATH = os.path.join(CONFIG_DIR, '%s.crt' % SERVER_NAME)
# width, height of each Z level
WIDTH = 512
HEIGHT = 512
# array of rects of starting position possibilities
STARTING_RECTS = [((50, 50), (60, 60))]
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# More advanced users, edit code below. 
#
'''

server_config
~~~~~~~~~~~~~

That's right... go ahead and modify it. It's just a config. It's executed
when the server is launched, and it's just going to look at SERVER_CONFIG
and read a few of its variables.

So, just jump in and edit the definition and variables of SERVER_CONFIG 
as desired. All the server will do is load that object and access certain
values, so you can put all your own logic here if you want to do anything
fancy.

'''

class LichServerConfig(object):
    '''
    Base class for a server configuration.
    Extend or use directly.
    '''

    def __init__(self):
        ''' initialize server configuration '''
        self.SERVER_NAME = SERVER_NAME
        self.SERVER_PORT = SERVER_PORT
        self.CONFIG_DIR = CONFIG_DIR
        self.DB_PATH = DB_PATH
        self.ADMIN_USERNAME = ADMIN_USERNAME
        self.USE_SSL = USE_SSL
        self.SSL_KEY_PATH = SSL_KEY_PATH
        self.SSL_CERT_PATH = SSL_CERT_PATH
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.STARTING_RECTS = STARTING_RECTS
        self.setup_logger()

    def setup_logger(self, debug=False):
        ''' Initialize logger '''
        log_file_fmt = '%(asctime)s:%(levelname)-8s:%(message)s'
        log_fmt = '[%(levelname)s] %(message)s'
        logging.basicConfig(
            level=logging.DEBUG if debug else LOGGER_LEVEL,
            filename=LOG_PATH,
            format=log_file_fmt,
        )
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(logging.Formatter(log_fmt))
        self.logger = logging.getLogger('cursed_lich')
        self.logger.addHandler(self.stream_handler)
        self.logger.setLevel(logging.DEBUG if debug else STDOUT_LEVEL)

    def set_debug_mode(self):
        self.logger.setLevel(logging.DEBUG)

    def starting_pos(self):
        rect = random.choice(self.STARTING_RECTS)
        x = random.randint(rect[0][0], rect[0][1])
        y = random.randint(rect[1][0], rect[1][1])
        return x, y

    class Z_Level(object):
        ''' inner class to describe names of z levels and geology '''
        MIDGAARD = 0
        ALFHEIM = 1
        JOTUNHEIM = 2
        NIFLHEIM = 3
        MUSPELHEIM = 4
        ASGARD = 5
        HEL = -1

        NAME = {
            0: 'midgaard',
            1: 'alfheim',
            2: 'jotunheim',
            3: 'niflheim',
            4: 'muspelheim',
            5: 'asgard',
            -1: 'hel',
        }

        @classmethod
        def get_name(cls, z_level):
            return cls.NAME[z_level]

    def __repr__(self):
        return ('NCursedServer(name=%(name)s, port=%(port)s, db=%(db)s, '
                'admin=%(admin)s)' % {
                    'name': self.SERVER_NAME,
                    'port': self.SERVER_PORT,
                    'db': self.DB_PATH,
                    'admin': self.ADMIN_USERNAME,
                })

    def __str__(self):
        return self.__repr__()

SERVER_CONFIG = LichServerConfig()

if __name__ == '__main__':
    pass
