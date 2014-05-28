# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import sys, collections

from pesky.defaults.errors import UndefinedDefault, DefaultsError

class Defaults(collections.Mapping):
    """
    Contains defaults data.  The defaults are obtained in the following order:
    First, entries are loaded from system/platform defaults (linux, windows, mac).
    Second, if a site module has been defined (such as by a distribution-specific
    package), then these entries override the system defaults, unless ignoresite
    is set to True.  Finally, if project is not None, then entries are loaded
    from the specified project pkg_resources.
    """
    def __init__(self, project=None, ignoresite=False):
        self._defaults = dict()
        # load system defaults
        from pesky.defaults.system import system_defaults
        for name,value in system_defaults().items():
            self._defaults[name] = value
        # load site overrides if the module exists
        if not ignoresite:
            try:
                from pesky.defaults.site import site_defaults
                for name,value in site_defaults().items():
                    self._defaults[name] = value
            except ImportError, e:
                pass
        # load package overrides
        if project is not None:
            from pesky.defaults.package import package_defaults
            for name,value in package_defaults(project).items():
                self._defaults[name] = value

    def get(self, name):
        """
        Get the default with the specified name.  if the entry doesn't exist,
        then raise UndefinedDefault exception.
        """
        try:
            return self._defaults[name]
        except KeyError:
            raise UndefinedDefault("default %s is undefined" % name)

    def getorelse(self, name, default=None):
        """
        Get the default with the specified name.  if the entry doesn't exist,
        then return the default, which is None by default.
        """
        try:
            return self._defaults[name]
        except KeyError:
            return default

    def has(self, name):
        """
        Return True if an entry exists with the specified name, otherwise False.
        """
        return name in self._defaults

    def __getitem__(self, name):
        return self._defaults[name]

    def __iter__(self):
        return iter(self._defaults)

    def __len__(self):
        return len(self._defaults)
