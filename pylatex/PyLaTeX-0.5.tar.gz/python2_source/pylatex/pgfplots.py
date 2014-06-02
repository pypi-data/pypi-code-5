# -*- coding: utf-8 -*-
u"""
    pylatex.pgfplots
    ~~~~~~~~~~~~~~~~

    This module implements the classes used to show plots.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""


from __future__ import absolute_import
from pylatex.base_classes import BaseLaTeXClass, BaseLaTeXNamedContainer
from pylatex.package import Package


class TikZ(BaseLaTeXNamedContainer):

    u"""Basic TikZ container class."""

    def __init__(self, data=None):
        packages = [Package(u'tikz')]
        super(TikZ, self).__init__(u'tikzpicture', data=data, packages=packages)
    __init__.func_annotations = {}


class Axis(BaseLaTeXNamedContainer):

    u"""PGFPlots axis container class, this contains plots."""

    def __init__(self, data=None, options=None):
        packages = [Package(u'pgfplots'), Package(u'compat=newest',
                                                 base=u'pgfplotsset')]

        super(Axis, self).__init__(u'axis', data=data, options=options, packages=packages)
    __init__.func_annotations = {}


class Plot(BaseLaTeXClass):

    u"""PGFPlot normal plot."""

    def __init__(self, name=None, func=None, coordinates=None, options=None):
        self.name = name
        self.func = func
        self.coordinates = coordinates
        self.options = options

        packages = [Package(u'pgfplots'), Package(u'compat=newest',
                                                 base=u'pgfplotsset')]

        super(Plot, self).__init__(packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the plot as a string in LaTeX syntax."""
        string = ur'\addplot'

        if self.options is not None:
            string += u'[' + self.options + u']'

        if self.coordinates is not None:
            string += u' coordinates {\n'

            for c in self.coordinates:
                string += u'(' + unicode(c[0]) + u',' + unicode(c[1]) + u')\n'
            string += u'};\n\n'

        elif self.func is not None:
            string += u'{' + self.func + u'};\n\n'

        if self.name is not None:
            string += ur'\addlegendentry{' + self.name + u'}\n'

        super(Plot, self).dumps()

        return string
    dumps.func_annotations = {}
