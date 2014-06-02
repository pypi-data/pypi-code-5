# -*- coding: utf-8 -*-
u"""
    pylatex.document
    ~~~~~~~

    This module implements the class that deals with the full document.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
import subprocess
from .package import Package
from .utils import dumps_list
from .base_classes import BaseLaTeXContainer
from io import open


class Document(BaseLaTeXContainer):

    u"""A class that contains a full latex document."""

    def __init__(self, filename=u'default_filename', documentclass=u'article',
                 fontenc=u'T1', inputenc=u'utf8', author=None, title=None,
                 date=None, data=None):
        self.filename = filename

        self.documentclass = documentclass

        fontenc = Package(u'fontenc', option=fontenc)
        inputenc = Package(u'inputenc', option=inputenc)
        packages = [fontenc, inputenc, Package(u'lmodern')]

        if title is not None:
            packages.append(Package(title, base=u'title'))
        if author is not None:
            packages.append(Package(author, base=u'author'))
        if date is not None:
            packages.append(Package(date, base=u'date'))

        super(Document, self).__init__(data, packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the document as a string in LaTeX syntax."""
        document = ur'\begin{document}'

        document += dumps_list(self)

        document += ur'\end{document}'

        super(Document, self).dumps()

        head = ur'\documentclass{' + self.documentclass + u'}'

        head += self.dumps_packages()

        return head + document
    dumps.func_annotations = {}

    def generate_tex(self):
        u"""Generates a .tex file."""
        newf = open(self.filename + u'.tex', u'w')
        self.dump(newf)
        newf.close()
    generate_tex.func_annotations = {}

    def generate_pdf(self, clean=True):
        u"""Generates a pdf"""
        self.generate_tex()

        command = u'pdflatex --jobname="' + self.filename + u'" "' + \
            self.filename + u'.tex"'

        subprocess.call(command, shell=True)

        if clean:
            subprocess.call(u'rm "' + self.filename + u'.aux" "' +
                            self.filename + u'.log" "' +
                            self.filename + u'.tex"', shell=True)
    generate_pdf.func_annotations = {}
