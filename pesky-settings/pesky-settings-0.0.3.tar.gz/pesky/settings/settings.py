# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import os, sys, getopt, datetime
from ConfigParser import RawConfigParser

from pesky.settings.parser import Parser
from pesky.settings.namespace import Namespace
from pesky.settings.errors import ConfigureError

class Settings(Parser):
    """
    Contains configuration loaded from the configuration file and
    parsed from command-line arguments.
    """

    def __init__(self, usage, version, description, subusage='Available subcommands:', section=None, appname=None, confbase='/etc/'):
        """
        :param usage: The usage string, displayed in --help output
        :type usage: str
        :param description: A short application description, displayed in --help output
        :type description: str
        :param subusage: If subcommands are specified, then display this message above
        :type subusage: str
        """
        if appname is not None:
            self.appname = appname
        else:
            self.appname = os.path.basename(sys.argv[0])
        if section is not None:
            self._section = section
        else:
            self._section = self.appname
        self._confbase = os.path.abspath(confbase)
        self._cwd = os.getcwd()
        Parser.__init__(self, None, self.appname, version, usage, description, subusage, self._section)
        self.add_option('c', 'config-file', 'config file',
            section=self._section, help="Load configuration from FILE", metavar="FILE"
            )

    def parse(self, argv=None, needsconfig=False):
        """
        Load configuration from the configuration file and from command-line arguments.

        :param argv: The argument vector, or None to use sys.argv
        :type argv: [str]
        :param needsconfig: True if the config file must be present for the application to function.
        :type needsconfig: bool
        :returns: A :class:`Namespace` object with the parsed settings
        :rtype: :class:`Namespace`
        """
        stack = list()
        options = RawConfigParser()
        args = list()
        overrides = RawConfigParser()
        try:
            if argv is None:
                argv = sys.argv
            overrides.add_section(self._section)
            overrides.set(self._section, 'config file', os.path.join(self._confbase, "%s.conf" % self.appname))
            # parse command line arguments
            stack,args = self._parse(argv[1:], overrides)
            # load configuration file
            config_file = overrides.get(self._section, 'config file')
            path = os.path.normpath(os.path.join(self._cwd, config_file))
            with open(path, 'r') as f:
                options.readfp(f, path)
        except getopt.GetoptError, e:
            raise ConfigureError(str(e))
        except EnvironmentError, e:
            if needsconfig:
                raise ConfigureError("failed to read configuration: %s", e.strerror)
        # merge command line settings with config file settings
        for section in overrides.sections():
            for name,value in overrides.items(section):
                if not options.has_section(section):
                    options.add_section(section)
                options.set(section, name, str(value))
        return Namespace(stack, options, args, self.appname, self._cwd, self._section)
