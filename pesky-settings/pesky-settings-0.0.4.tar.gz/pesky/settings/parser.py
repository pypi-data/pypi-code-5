# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import os, sys, getopt, datetime
from ConfigParser import RawConfigParser

from pesky.settings.option import *
from pesky.settings.errors import ConfigureError

class Parser(object):
    """
    :param parent:
    :type parent: :class:`Parser`
    :param name:
    :type name: str
    :param usage:
    :type usage: str
    :param description:
    :type description: str
    :param subusage:
    :type subusage: str
    """
    def __init__(self, parent, name, version, usage, description, subusage, section):
        self._parent = parent
        self.name = name
        self.version = version
        self.usage = usage
        self.description = description
        self.subusage = subusage
        self.section = section
        self._subcommands = {}
        self._options = {}
        self._optslist = []

    def add_subcommand(self, name, usage, description, version=None, subusage='Available subcommands:'):
        """
        Add a subcommand to the parser.

        :param name:
        :type name: str
        :param usage:
        :type usage: str
        :param description:
        :type description: str
        :param subusage:
        :type subusage: str
        """
        if name in self._subcommands:
            raise ConfigureError("subcommand '%s' is already defined" % name)
        if version is None:
            version = self.version
        subcommand = Parser(self, name, version, usage, description, subusage, None)
        self._subcommands[name] = subcommand
        return subcommand

    def _lookup_section(self):
        sections = list()
        parser = self
        while parser is not None:
            if parser.section is not None:
                name = parser.section
            else:
                name = parser.name
            sections.insert(0, name)
            parser = parser._parent
        return ':'.join(sections)

    def add(self, o):
        """
        Add a command-line option or switch.

        :param o: o
        :type o: :class:`Option`
        """
        if not isinstance(o, Option):
            raise TypeError("%s is not an instance of type Option" % o)
        if o.shortname in self._options:
            raise RuntimeError("-%s is already defined" % o.shortname)
        if o.longname in self._options:
            raise RuntimeError("--%s is already defined" % o.longname)
        if o.section is None:
            o.section = self._lookup_section()
        self._options["-%s" % o.shortname] = o
        self._options["--%s" % o.longname] = o
        self._optslist.append(o)

    def add_option(self, shortname, longname, override, section=None, help=None, metavar=None):
        """
        Add a command-line option to be parsed.  An option (as opposed to a switch)
        is required to have an argument.

        :param shortname: the one letter option name.
        :type shortname: str
        :param longname: the long option name.
        :type longname: str
        :param override: Override the specified section key.
        :type override: str
        :param section: Override the key in the specified section.
        :type section: str
        :param help: The help string, displayed in --help output.
        :type help: str
        :param metavar: The variable displayed in the help string
        :type metavar: str
        """
        self.add(Option(shortname, longname, override, section, help, metavar))

    def add_shortoption(self, shortname, override, section=None, help=None, metavar=None):
        self.add(ShortOption(shortname, override, section, help, metavar))

    def add_longoption(self, longname, override, section=None, help=None, metavar=None):
        self.add(LongOption(longname, override, section, help, metavar))

    def add_switch(self, shortname, longname, override, section=None, reverse=False, help=None):
        """
        Add a command-line switch to be parsed.  A switch (as opposed to an option)
        has no argument.

        :param shortname: the one letter option name.
        :type shortname: str
        :param longname: the long option name.
        :type longname: str
        :param override: Override the specified section key.
        :type override: str
        :param section: Override the key in the specified section.
        :type section: str
        :param reverse: If True, then the meaning of the switch is reversed.
        :type reverse: bool
        :param help: The help string, displayed in --help output.
        :type help: str
        """
        self.add(Switch(shortname, longname, override, section, reverse, help))

    def add_shortswitch(self, shortname, override, section=None, reverse=False, help=None):
        self.add(ShortSwitch(shortname, override, section, reverse, help))

    def add_longswitch(self, longname, override, section=None, reverse=False, help=None):
        self.add(LongSwitch(longname, override, section, reverse, help))

    def _parse(self, argv, store):
        """
        Parse the command line specified by argv, and store the options
        in store.
        """
        shortnames = ''.join([o.shortident for o in self._optslist if o.shortname != ''])
        longnames = [o.longident for o in self._optslist if o.longname != '']
        longnames += ['help', 'version']
        if len(self._subcommands) == 0:
            opts,args = getopt.gnu_getopt(argv, shortnames, longnames)
        else:
            opts,args = getopt.getopt(argv, shortnames, longnames)
        seen = set()
        for opt,value in opts:
            if opt == '--help': self._usage()
            if opt == '--version': self._version()
            o = self._options[opt]
            if o in seen:
                if not o.recurring:
                    raise ConfigureError("%s is not a recurring option")
                seen.add(o)
            if not store.has_section(o.section):
                store.add_section(o.section)
            o.set(store, value)
        if len(self._subcommands) > 0:
            if len(args) == 0:
                raise ConfigureError("no subcommand specified")
            subcommand = args[0]
            args = args[1:]
            if not subcommand in self._subcommands:
                raise ConfigureError("no subcommand named '%s'" % subcommand)
            stack,args = self._subcommands[subcommand]._parse(args, store)
            stack.insert(0, subcommand)
            return stack,args
        return [], args

    def _usage(self):
        """
        Display a usage message and exit.
        """
        commands = []
        c = self
        while c != None:
            commands.insert(0, c.name)
            c = c._parent
        print "Usage: %s %s" % (' '.join(commands), self.usage)
        print 
        # display the description, if it was specified
        if self.description != None and self.description != '':
            print self.description
            print
        # display options
        if len(self._optslist) > 0:
            options = []
            maxlength = 0
            for o in self._optslist:
                spec = []
                if o.shortname != '':
                    spec.append("-%s" % o.shortname)
                if o.longname != '':
                    spec.append("--%s" % o.longname)
                if isinstance(o, Switch):
                    spec = ','.join(spec)
                elif isinstance(o, Option):
                    spec = ','.join(spec) + ' ' + o.metavar
                options.append((spec, o.help))
                if len(spec) > maxlength:
                    maxlength = len(spec)
            for spec,help in options: 
                print " %s%s" % (spec.ljust(maxlength + 4), help)
            print
        # display subcommands, if there are any
        if len(self._subcommands) > 0:
            print self.subusage
            print
            for name,parser in sorted(self._subcommands.items()):
                print " %s" % name
            print
        sys.exit(0)

    def _version(self):
        """
        Display the version and exit.
        """
        c = self
        while c._parent != None: c = c._parent
        print "%s %s" % (c.name, self.version)
        sys.exit(0)
