#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Shared constants and funtions."""

# Python 3 compatibility
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import date
import sys
from os import path
import pickle
from pkg_resources import resource_filename
import __init__ as globalcfg


LANG = globalcfg.LANG

if LANG == 'PT':
    VERSION = ' versão '
else:
    VERSION = ' version '

# set correct path to all data files
try:
    # DATA_PATH = X:\PyhtonXX\Lib\site-packages\daysgrounded
    DATA_PATH = resource_filename(__name__, globalcfg.USAGE_FILE)
    DATA_PATH = DATA_PATH.replace(globalcfg.USAGE_FILE, '')
except:  # ToDo: find what exception happens here
    # if current module is frozen, use library.zip path
    # DATA_PATH = exe location
    if hasattr(sys, 'frozen'):
        ##DATA_PATH = sys.prefix
        ##DATA_PATH.strip('/')
        DATA_PATH = path.dirname(sys.executable)
        DATA_PATH += '/'

USAGE_FILE = DATA_PATH + globalcfg.USAGE_FILE
BANNER_FILE = DATA_PATH + globalcfg.BANNER_FILE
LICENSE_FILE = DATA_PATH + globalcfg.LICENSE_FILE

DATA_FILE = DATA_PATH + 'daysgrounded.pkl'
LOG = True
LOG_FILE = DATA_PATH + 'daysgrounded_log.pkl'
MAX_DAYS = 99
MAX_DAYS_STR = str(MAX_DAYS)


def update_file(childs, last_upd):
    """
    Update data file and log file.

    The log file creates an history to be used in the future.
    """
    with open(DATA_FILE, 'wb') as file_:
        pickle.dump(childs, file_)
        pickle.dump(last_upd, file_)
        ##pickle.dump([childs, last_upd], f)
    if LOG:
        with open(LOG_FILE, 'ab') as file_:
            pickle.dump([childs, last_upd], file_)


def create_file():
    """Create new data file and log file."""
    # use lower case letters or names
    childs = {'t': 0, 's': 0}
    last_upd = date.today()
    update_file(childs, last_upd)
    return childs, last_upd


def read_file():
    """Reads and returns childs and last_upd from the data file."""
    with open(DATA_FILE, 'rb') as file_:
        childs = pickle.load(file_)
        last_upd = pickle.load(file_)
        ##[childs, last_upd] = pickle.load(f)
    return childs, last_upd


def usage():
    """Returns usage text, read from a file."""
    with open(USAGE_FILE) as file_:
        return file_.read()


def banner():
    """Returns banner text."""
    banner_txt = ('\n' + globalcfg.NAME + VERSION + globalcfg.VERSION +
                  ', ' + globalcfg.COPYRIGHT + '\n')
    with open(BANNER_FILE) as file_:
        return banner_txt + file_.read()


def version():
    """Returns version."""
    return globalcfg.VERSION


def license_():
    """Returns license text, read from a file."""
    with open(LICENSE_FILE) as file_:
        return file_.read()


def auto_upd_datafile(childs, last_upd):
    """Automatic update based on current date vs last update date."""
    right_now = date.today()
    days_to_remove = (right_now - last_upd).days  # convert to days and assign
    for child in childs:
        childs[child] -= days_to_remove
        childs[child] = max(0, childs[child])
    update_file(childs, right_now)
    return right_now


def open_create_datafile():
    """Opens datafile if it exists, otherwise creates it."""
    if path.isfile(DATA_FILE):  # if file exists
        childs, last_upd = read_file()
    else:
        childs, last_upd = create_file()
    return childs, last_upd


if __name__ == '__main__':
    #import doctest
    #doctest.testmod(verbose=True)
    pass
