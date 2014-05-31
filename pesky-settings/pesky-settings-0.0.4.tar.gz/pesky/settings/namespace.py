# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

from pesky.settings.section import Section
from pesky.settings.args import parse_args
from pesky.settings.errors import ConfigureError

class Namespace(object):
    """
    """
    def __init__(self, stack, options, args, appname, cwd, section):
        """
        :param stack:
        :type stack: [str]
        :param options:
        :type options: :class:`ConfigParser.RawConfigParser`
        :param args:
        :type args: [str]
        :param appname:
        :type appname: str
        :param cwd:
        :type cwd: str
        """
        self._stack = stack
        self._options = options
        self._args = args
        self._appname = appname
        self._cwd = cwd
        self._section = section

    @property
    def appname(self):
        return self._appname

    @property
    def cwd(self):
        return self._cwd

    @property
    def args(self):
        return list(self._args)

    def get_args(self, *spec, **kwargs):
        """
        Returns a list containing command-line arguments conforming to *spec.
        if the number of command arguments is less than minimum or greater
        than maximum, or if any argument cannot be validated, ConfigureError
        is raised.  Any optional arguments which are not specified are passed
        unmodified.

        :param spec: a list of validator functions
        :type spec: [callable]
        :param minimum: The number of required arguments
        :type: int
        :param maximum: The numer of required + optional arguments
        :type maxmimum: int
        :param names: a list of argument names corresponding to each validator
        :type names: [str]
        :returns: a tuple containing arguments conforming to spec
        :rtype: [object]
        """
        return parse_args(self.args, *spec, **kwargs)

    def pop_stack(self):
        if len(self._stack) > 0:
            return self._stack.pop(0)
        return None

    def has_section(self, name):
        """
        Returns True if the specified section exists, otherwise False.

        :param name: The section name.
        :type name: str
        :returns: True or False.
        :rtype: [bool]
        """
        return self._options.has_section(name)

    def get_section(self, name=None):
        """
        Get the section with the specified name, or the section named appname
        if name is None.  Note if the section does not exist, this method still
        doesn't fail, it returns an empty Section.

        :param name: The section name.
        :type name: str
        :returns: The specified section.
        :rtype: :class:`Section`
        """
        name = self._section if name is None else name
        return Section(name, self._options, self._cwd)

    def list_sections(self):
        """
        Return a list of all sections.

        :returns: A list of all sections.
        :rtype: :[class:`Section`]
        """
        sections = []
        for name in self._options.sections():
            sections.append(Section(name, self._options, self._cwd))
        return sections

    def find_sections(self, startswith):
        """
        Return a list of all sections which start with the specified prefix.

        :param startsWith: The section name prefix.
        :type name: str
        :returns: A list of matching sections.
        :rtype: [:class:`Section`]
        """
        sections = []
        for name in [s for s in self._options.sections() if s.startswith(startswith)]:
            sections.append(Section(name, self._options, self._cwd))
        return sections
