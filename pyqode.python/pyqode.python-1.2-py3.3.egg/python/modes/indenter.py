#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
Contains the python indenter.
"""
from pyqode.core import IndenterMode
from pyqode.qt import QtGui


class PyIndenterMode(IndenterMode):
    """
    Implements python specific indentation, tab/back-tab always
    indents/unindents the **whole** line. This replace the default IndenterMode
    which we found to be better suited for python code editing.
    """

    def indent(self):
        cursor = self.editor.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)
        self.indentSelection(cursor)

    def unIndent(self):
        cursor = self.editor.textCursor()
        assert isinstance(cursor, QtGui.QTextCursor)
        if not cursor.hasSelection():
            cursor.select(cursor.LineUnderCursor)
        self.unIndentSelection(cursor)