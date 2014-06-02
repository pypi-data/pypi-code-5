# -*- coding: utf-8 -*-
u"""
    pylatex.base_classes
    ~~~~~~~~~~~~~~~~~~~~

    This module implements base classes with inheritable functions for other
    LaTeX classes.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
from UserList import UserList
from ordered_set import OrderedSet
from pylatex.utils import dumps_list


class BaseLaTeXClass(object):

    u"""A class that has some basic functions for LaTeX functions."""

    def __init__(self, packages=None):
        if packages is None:
            packages = []

        self.packages = OrderedSet(packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the class as a string in LaTeX syntax."""
    dumps.func_annotations = {}

    def dump(self, file_):
        u"""Writes the LaTeX representation of the class to a file."""
        file_.write(self.dumps())
    dump.func_annotations = {}

    def dumps_packages(self):
        u"""Represents the packages needed as a string in LaTeX syntax."""
        return dumps_list(self.packages)
    dumps_packages.func_annotations = {}

    def dump_packages(self, file_):
        u"""Writes the LaTeX representation of the packages to a file."""
        file_.write(self.dumps_packages())
    dump_packages.func_annotations = {}


class BaseLaTeXContainer(BaseLaTeXClass, UserList):

    u"""A base class that can cointain other LaTeX content."""

    def __init__(self, data=None, packages=None):
        if data is None:
            data = []

        self.data = data

        super(BaseLaTeXContainer, self).__init__(packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the container as a string in LaTeX syntax."""
        self.propegate_packages()
    dumps.func_annotations = {}

    def propegate_packages(self):
        u"""Makes sure packages get propegated."""
        for item in self.data:
            if isinstance(item, BaseLaTeXClass):
                for p in item.packages:
                    self.packages.add(p)
    propegate_packages.func_annotations = {}

    def dumps_packages(self):
        u"""Represents the packages needed as a string in LaTeX syntax."""
        self.propegate_packages()
        return dumps_list(self.packages)
    dumps_packages.func_annotations = {}


class BaseLaTeXNamedContainer(BaseLaTeXContainer):

    u"""A base class for containers with one of a basic begin end syntax"""

    def __init__(self, name, data=None, packages=None, options=None):
        self.name = name
        self.options = options

        super(BaseLaTeXNamedContainer, self).__init__(data=data, packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the named container as a string in LaTeX syntax."""
        string = ur'\begin{' + self.name + u'}\n'

        if self.options is not None:
            string += u'[' + self.options + u']'

        string += dumps_list(self)

        string += ur'\end{' + self.name + u'}\n'

        super(BaseLaTeXNamedContainer, self).dumps()

        return string
    dumps.func_annotations = {}
