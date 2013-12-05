# coding=utf-8
"""
This file will help to generate settings for a
heroku based django application easily. import *
from this file will automatically generate database
and email settings for heroku.


Database Settings
=================
Database settings will be parsed from the
herok config files. There are many solutions
for databases in heroku. They will be used as
given below.

Order
-----
1. Clear DB Database
2. Heroku Shared PG Database

Email Settings
==============
Currently send grid settings will be generated
automatically.

TODO:
Need more settings.

"""
__author__ = 'ajumell'
from send_grid_settings import has_send_grid
from database import has_clear_db
from django_helpers.helpers.settings.gmail_settings import has_gmail


if has_clear_db():
    from clear_db_settings import DATABASES
else:
    pass

if has_send_grid():
    from send_grid_settings import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT, EMAIL_USE_TLS
elif has_gmail():
    from django_helpers.helpers.settings.gmail_settings import EMAIL_HOST, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, EMAIL_PORT, EMAIL_USE_TLS
