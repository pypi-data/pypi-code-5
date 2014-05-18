#-*- coding: utf-8 -*-

import os

# Basic server config
TORNADO_PORT = 8888
BASE_URL = 'http://localhost:%s' % TORNADO_PORT
STATIC_URL = '/static/'
CORS_ORIGINS = '*'
DEBUG = True

# database settings
DATABASE = {'default': {'host': 'localhost',
                        'port': 27017,
                        'db': 'pyrocumulus-dev'}}


# directories containing static files
# static dir for functional tests
basedir = os.path.abspath(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../'))
static_dir = os.path.join(basedir, 'functional_tests')
static_dir = os.path.join(static_dir, 'testdata/')
STATIC_DIRS = [static_dir]

# directories containing templates
TEMPLATE_DIRS = []

# application to be served by tornado
APPLICATIONS = []
