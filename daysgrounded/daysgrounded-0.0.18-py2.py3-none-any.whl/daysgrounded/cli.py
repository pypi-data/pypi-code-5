#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Processes command line arguments and updates child's records."""

# Python 3 compatibility
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import date
import sys
import colorama
import shared


if shared.LANG == 'PT':
    WRONG_ARG = 'Erro: argumento incorreto '
else:
    WRONG_ARG = 'Err: incorrect argument '


def print_state(childs, last_upd):
    """Prints current state for each child."""
    for child in childs:
        print(child, childs[child])
    print(str(last_upd))


def man_upd(argv, childs, last_upd):
    """
    Manual update based on args.

    First it checks all args and only if all are correct are they processed.
    """
    arg_nok = ''
    args_ok = False

    # check args
    for arg in argv:
        if '-' in arg:
            child, days = str.lower(arg).split('-')
        elif '+' in arg:
            child, days = str.lower(arg).split('+')
        else:
            arg_nok = arg
            args_ok = False
            break

        try:
            days = int(days)
        except ValueError:  # as err:
            arg_nok = arg
            args_ok = False
            break

        if ((child in childs) and
           (-shared.MAX_DAYS <= days <= shared.MAX_DAYS)):
            args_ok = True
        else:
            arg_nok = arg
            args_ok = False
            break

    if args_ok:  # process args
        print_state(childs, last_upd)
        for arg in argv:
            if '-' in arg:
                child, days = str.lower(arg).split('-')
                days = -int(days)
            elif '+' in arg:
                child, days = str.lower(arg).split('+')
                days = int(days)

            childs[child] += days
            if childs[child] > 0:
                childs[child] = min(shared.MAX_DAYS, childs[child])
            else:
                childs[child] = max(0, childs[child])
        last_upd = date.today()
        shared.update_file(childs, last_upd)
        print_state(childs, last_upd)
    else:
        print(colorama.Fore.RED + WRONG_ARG +
              arg_nok + '\n')
        print(colorama.Fore.RESET + shared.usage())


def auto_upd(childs, last_upd):
    """Automatic update based on current date vs last update date."""
    print_state(childs, last_upd)
    last_upd = shared.auto_upd_datafile(childs, last_upd)
    print_state(childs, last_upd)


def start(argv):
    """Print banner, read/create data & log file and process args."""
    colorama.init()

    print(shared.banner())
    childs, last_upd = shared.open_create_datafile()

    arg0 = str.lower(argv[0])
    if arg0 in ['-h', '--help']:
        print(shared.usage())
    elif arg0 in ['-v', '--version']:
        print('Versão', shared.version())
    elif arg0 in ['-l', '--license']:
        print(shared.license_())
    elif arg0 in ['-a', '--auto']:
        auto_upd(childs, last_upd)
    else:
        man_upd(argv, childs, last_upd)

    sys.exit(0)  # ToDo: other return codes


if __name__ == '__main__':
    #import doctest
    #doctest.testmod(verbose=True)
    pass
