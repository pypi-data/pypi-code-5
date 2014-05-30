# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import os, sys, getopt, datetime
from ConfigParser import RawConfigParser

class UnittestSettings(Settings):
    """
    Subclass of Settings which loads configuration from a dict of dicts.  Only
    useful for unit tests.
    """
    def __init__(self, version='', usage='', description='', appname=''):
        """
        :param usage: The usage string, displayed in --help output.
        :type usage: str
        :param description: A short application description, displayed in --help output.
        :type description: str
        :param appname: The application name.
        :type appname: str
        """
        Parser.__init__(self, appname, version, usage, description)
        self.appname = appname
        self._config = RawConfigParser()
        self._overrides = RawConfigParser()
        self._cwd = os.getcwd()
        self._overrides.add_section('settings')
        self._overrides.set('settings', 'config file', "/etc/mandelbrot/%s.conf" % self.appname)
        self.addOption('c', 'config-file', 'settings', 'config file',
            help="Load configuration from FILE", metavar="FILE")

    def load(self, sections, cmdline=[]):
        """
        Load the configuration from the specified dict.

        :param sections: A dict whose keys are section names, and whose values are
          dicts containing option key-value pairs.
        :type sections: dict
        :param cmdline: A list of command line arguments.  Note this list excludes
          the executable name at cmdline[0].
        :type cmdline: list
        """
        # parse command line arguments
        self._parser,self._args = self._parse(cmdline, self._overrides)
        for sectionname,kvs in sections.items():
            self._config.add_section(sectionname)
            for key,value in kvs.items():
                self._config.set(sectionname, key, value)
        # merge command line settings with config file settings
        for section in self._overrides.sections():
            for name,value in self._overrides.items(section):
                if not self._config.has_section(section):
                    self._config.add_section(section)
                self._config.set(section, name, str(value))
