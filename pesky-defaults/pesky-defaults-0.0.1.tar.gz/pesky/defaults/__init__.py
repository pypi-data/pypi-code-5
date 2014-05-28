# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

__version__ = (0, 0, 1)

def versionstring():
    """
    Return the version number as a string.
    """
    return "%i.%i.%i" % __version__


from pesky.defaults.defaults import Defaults
from pesky.defaults.errors import DefaultsError, UndefinedDefault
