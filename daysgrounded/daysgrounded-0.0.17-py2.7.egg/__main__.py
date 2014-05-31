#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Manage child(s) grounded days.

   If there are any command line arguments it calls the cli module.
   Otherwise the gui module.
   See usage.txt for command line usage.
"""

# Python 3 compatibility
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
#import os

import cli
import gui


def main():
    """Start CLI or GUI"""
    if sys.argv[1:]:  # any args?
        cli.start(sys.argv[1:])
    else:
        gui.start()

if __name__ == '__main__':
    sys.exit(main())
