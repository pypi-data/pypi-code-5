#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module contains the definition of the SDL symbols,
    including geometry and specific symbol behaviour when needed.

    All symbols inherit the generic Vertical- and Horizontal-
    Symbol classes defined in the "genericSymbols.py" module.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
           'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol',
           'Procedure', 'ProcedureStart', 'ProcedureStop', 'ASN1Viewer']

from genericSymbols import(
        HorizontalSymbol, VerticalSymbol, Connection, Comment)

from PySide.QtCore import Qt, QPoint, QRect, QRectF
from PySide.QtGui import(QPainterPath, QBrush, QColor, QPolygon,
        QRadialGradient, QPainter, QPolygonF, QPen)

import ogParser
import ogAST

import traceback
import logging

LOG = logging.getLogger('sdlSymbols')


# SDL-specific: reserved keywords, to be highlighted in textboxes
# Two kind of formatting are possible: black bold, and red bold
SDL_BLACKBOLD = ['\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT', 'FPAR', 'TODO', 'FIXME', 'XXX',
                'CHECKME', 'PROCEDURE', 'EXTERNAL', 'IN', 'OUT', 'TIMER',
                'SET_TIMER', 'RESET_TIMER')]

SDL_REDBOLD = ['\\b{word}\\b'.format(word=word) for word in (
              'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE',
              'TASK', 'PROCESS', 'LABEL', 'JOIN', 'CONNECTION')]


# pylint: disable=R0904
class Input(HorizontalSymbol, object):
    ''' SDL INPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Input',  'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    completion_list = set()

    common_name = 'input_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, parent=None, ast=None):
        ''' Create the INPUT symbol '''
        ast = ast or ogAST.Input()
        self.branch_entrypoint = None
        super(Input, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        gradient = QRadialGradient(50, 50, 50, 50, 50)
        gradient.setColorAt(0, QColor(255, 240, 170))
        gradient.setColorAt(1, Qt.white)
        self.setBrush(QBrush(gradient))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def check_syntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntax_errors, ___, ____, _____ = self.parser.parseSingleElement(
                self.common_name, self.pr())
        try:
            # LOG.error('\n'.join(syntax_errors))
            self.scene().raise_syntax_errors(syntax_errors)
        except AttributeError:
            LOG.debug('raise_syntax_error raised an exception')

    def insert_symbol(self, parent, x, y):
        ''' Insert Input symbol - propagate branch Entry point '''
        # Make sure that parent is a state, not a sibling input
        item_parent = (parent if not isinstance(parent, Input)
                       else parent.parentItem())
        self.branch_entrypoint = item_parent.branch_entrypoint
        super(Input, self).insert_symbol(item_parent, x, y)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width - 15, height / 2)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Input, self).set_shape(width, height)

    def pr(self):
        ''' Return the PR notation of the single INPUT symbol '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        return('/* CIF INPUT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'INPUT {i}{comment}'.format(
                    hlink=repr(self.text), i=str(self),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))

    def __repr__(self):
        ''' Return the complete Input branch in PR format '''
        result = [self.pr()]
        # Recursively return the complete branch below the INPUT
        next_symbol = self.next_aligned_symbol()
        while next_symbol:
            result.append(repr(next_symbol))
            next_symbol = next_symbol.next_aligned_symbol()
        return '\n'.join(result)


# pylint: disable=R0904
class Output(VerticalSymbol, object):
    ''' SDL OUTPUT Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'output'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output()
        super(Output, self).__init__(parent=parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)

        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width - 15, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width - 15, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Output, self).set_shape(width, height)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        return ('/* CIF OUTPUT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'OUTPUT {o}{comment}'.format(
                    hlink=repr(self.text), o=str(self),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


# pylint: disable=R0904
class Decision(VerticalSymbol, object):
    ''' SDL DECISION Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall', 'Output',
                        'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'decision'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD + ['\\b{}\\b'.format(word)
                                   for word in ('AND', 'OR')]
    redbold = SDL_REDBOLD
    completion_list = {'length', 'present'}

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Decision()
        # Define the point where all branches of the decision can join again
        self.connectionPoint = QPoint(ast.width / 2, ast.height + 30)
        super(Decision, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QColor(255, 255, 202))
        self.minDistanceToSymbolAbove = 0
        self.parser = ogParser
        self.text_alignment = Qt.AlignHCenter
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    @property
    def terminal_symbol(self):
        '''
            Compute dynamically if the item is terminal by checking
            if all its branches end with a terminator
        '''
        for branch in self.branches():
            if not branch.last_branch_item.terminal_symbol:
                return False
        else:        
            return True

    def branches(self):
        ''' Return the list of decision answers (as a generator) '''
        return (branch for branch in self.childSymbols()
                if isinstance(branch, DecisionAnswer))

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def check_syntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntax_errors, ___, ____, _____ = self.parser.parseSingleElement(
                self.common_name, self.pr(recursive=False))
        try:
            # LOG.error('\n'.join(syntax_errors))
            self.scene().raise_syntax_errors(syntax_errors)
        except AttributeError:
            LOG.debug('raise_syntax_error raised an exception')

    def set_shape(self, width, height):
        ''' Define polygon points to draw the symbol '''
        path = QPainterPath()
        path.moveTo(width / 2, 0)
        path.lineTo(width, height / 2)
        path.lineTo(width / 2, height)
        path.lineTo(0, height / 2)
        path.lineTo(width / 2, 0)
        self.setPath(path)
        super(Decision, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' On resize event, make sure connection points are updated '''
        delta_y = self.boundingRect().height() - rect.height()
        super(Decision, self).resize_item(rect)
        self.connectionPoint.setX(self.boundingRect().center().x())
        self.connectionPoint.setY(self.connectionPoint.y() - delta_y)
        self.update_connections()

    def update_connections(self):
        ''' Redefined - update arrows shape below connection point '''
        super(Decision, self).update_connections()
        for branch in self.branches():
            for cnx in branch.last_branch_item.connections():
                cnx.reshape()

    def updateConnectionPointPosition(self):
        ''' Compute the joining point of decision branches '''
        new_y = 0
        new_x = self.boundingRect().width() / 2.0
        answers = False
        for branch in self.branches():
            answers = True
            last_cnx = None
            last = branch.last_branch_item
            try:
                # To compute the branch length, we must keep only the symbols,
                # so we must remove the last connection (if any)
                last_cnx, = (c for c in last.childItems() if
                    isinstance(c, Connection) and not
                    isinstance(c.child, (Comment, HorizontalSymbol)))
                last_cnx.setParentItem(None)
            except ValueError:
                pass
            try:
                # Disconnect the comment of the last item so that
                # it's size is not taken into account
                last.comment.setParentItem(None)
                last.comment.connection.setParentItem(None)
            except AttributeError:
                pass
            branch_len = branch.y() + (
                    branch.boundingRect() |
                    branch.childrenBoundingRect()).height()
            try:
                last_cnx.setParentItem(last)
            except AttributeError:
                pass
            try:
                # Reconnect the comment of the last item
                last.comment.setParentItem(last)
                last.comment.connection.setParentItem(last)
            except AttributeError:
                pass
            # If last item was a decision, use its connection point
            # position to get the length of the branch:
            try:
                branch_len = (last.connectionPoint.y() +
                        self.mapFromScene(0, last.scenePos().y()).y())
            except AttributeError:
                pass
            # Rounded with int() -> mandatory when view scale has changed
            new_y = int(max(new_y, branch_len))
        if not answers:
            new_y = int(self.boundingRect().height())
        new_y += 15
        delta = new_y - self.connectionPoint.y()
        self.connectionPoint.setY(new_y)
        self.connectionPoint.setX(new_x)
        if delta != 0:
            child = self.next_aligned_symbol()
            try:
                child.moveBy(0, delta)
            except AttributeError:
                pass
        self.update_connections()

    def pr(self, recursive=True):
        ''' Get PR notation of a decision (possibly recursively) '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        result = ['/* CIF DECISION ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'DECISION {d}{comment}'.format(
                    hlink=repr(self.text), d=str(self),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment)]
        if recursive:
            for answer in self.branches():
                if str(answer).lower().strip() == 'else':
                    result.append(repr(answer))
                else:
                    result.insert(1, repr(answer))
        result.append('ENDDECISION;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the PR notation for the decision and all answers '''
        return self.pr(recursive=True)


# pylint: disable=R0904
class DecisionAnswer(HorizontalSymbol, object):
    ''' If Decision is a "switch", DecisionAnswer is a "case" '''
    _insertable_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                        'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'alternative_part'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Answer()
        # temp, FIXME
        self.width, self.height = ast.width, ast.height
        self.terminal_symbol = False
        # last_branch_item is used to compute branch length
        # for the connection point positionning
        self.last_branch_item = self
        super(DecisionAnswer, self).__init__(parent,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        #self.setPen(QColor(0, 0, 0, 0))
        self.branch_entrypoint = self
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def check_syntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntax_errors, ___, ____, _____ = self.parser.parseSingleElement(
                self.common_name, self.pr(recursive=False))
        try:
            self.scene().raise_syntax_errors(syntax_errors)
        except:
            LOG.debug('raise_syntax_error raised an exception')

    def insert_symbol(self, parent, x, y):
        ''' ANSWER-specific insersion behaviour: link to connection point '''
        if not parent:
            return
        # Make sure that parent is a state, not a sibling input
        item_parent = (parent if not isinstance(parent, DecisionAnswer)
                       else parent.parentItem())
        super(DecisionAnswer, self).insert_symbol(item_parent, x, y)
        self.last_branch_item.connectionBelow = Connection(
                self.last_branch_item, item_parent, connectionPoint=True)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def set_shape(self, width, height):
        ''' ANSWER has round, disjoint sides - does not fit in a polygon '''
        self.width, self.height = width, height
        path = QPainterPath()
        left = QRect(0, 0, 35, height)
        right = QRect(width - 35, 0, 35, height)
        path.arcMoveTo(left, 125)
        path.arcTo(left, 125, 110)
        path.arcMoveTo(right, -55)
        path.arcTo(right, -55, 110)
        path.moveTo(width, height)
        self.setPath(path)
        super(DecisionAnswer, self).set_shape(width, height)

    def pr(self, recursive=True):
        ''' Return the PR string for the symbol, possibly recursively '''
        ans = str(self)
        if ans.lower().strip() != 'else':
            ans = '({ans})'.format(ans=ans)
        pos = self.scenePos()
        result = ['/* CIF ANSWER ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{a}:'.format(a=ans, hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()))]
        if recursive:
            next_symbol = self.next_aligned_symbol()
            while next_symbol:
                result.append(repr(next_symbol))
                next_symbol = next_symbol.next_aligned_symbol()
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        return self.pr()


# pylint: disable=R0904
class Join(VerticalSymbol, object):
    ''' JOIN symbol (GOTO) '''
    auto_expand = False
    arrow_head = True
    common_name = 'terminator_statement'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        if not ast:
            ast = ogAST.Terminator(defName='Goto')
            ast.pos_y = 0
            ast.width = 50
            ast.height = 50
        super(Join, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = True
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def resize_item(self, rect):
        ''' Redefinition of the resize item (block is a square) '''
        size = min(rect.width(), rect.height())
        rect.setWidth(size)
        rect.setHeight(size)
        super(Join, self).resize_item(rect) 

    def set_shape(self, width, height):
        ''' Define the bouding rectangle of the JOIN symbol '''
        circ = min(width, height)
        path = QPainterPath()
        path.addEllipse(0, 0, circ, circ)
        self.setPath(path)
        super(Join, self).set_shape(width, height)

    def __repr__(self):
        ''' Return the PR string for the join '''
        pos = self.scenePos()
        return('/* CIF JOIN ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'JOIN {label};'.format(label=str(self),
                    hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


class ProcedureStop(Join, object):
    ''' Procedure STOP symbol - very similar to JOIN '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    def __init__(self, parent=None, ast=None):
        if not ast:
            ast = ogAST.Terminator(defName='ret')
            ast.pos_y = 0
            ast.width = 50
            ast.height = 50
        super(ProcedureStop, self).__init__(parent, ast)
    completion_list = set()

    def set_shape(self, width, height):
        ''' Define the symbol shape '''
        circ = min(width, height)
        path = QPainterPath()
        path.addEllipse(0, 0, circ, circ)
        point1 = path.pointAtPercent(0.625)
        point2 = path.pointAtPercent(0.125)
        point3 = path.pointAtPercent(0.875)
        point4 = path.pointAtPercent(0.375)
        path.moveTo(point1)
        path.lineTo(point2)
        path.moveTo(point3)
        path.lineTo(point4)        
        self.setPath(path)
        # call Join superclass, otherwise symbol will take Join shape
        super(Join, self).set_shape(circ, circ)

    def __repr__(self):
        ''' Return the PR string for this symbol '''
        pos = self.scenePos()
        return('/* CIF STOP ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'STOP;'.format(hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


# pylint: disable=R0904
class Label(VerticalSymbol, object):
    ''' LABEL symbol '''
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'label'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    # Symbol must not use antialiasing, otherwise the middle line is too thick
    _antialiasing = False
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Label()
        super(Label, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setPen(QPen(Qt.blue))
        self.terminal_symbol = False
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def set_shape(self, width, height):
        ''' Define the shape of the LABEL symbol '''
        #print traceback.print_stack()
        path = QPainterPath()
        path.addEllipse(0, height / 2, width / 4, height / 2)
        path.moveTo(width / 4, height * 3 / 4)
        path.lineTo(width / 2, height * 3 / 4)
        # Add arrow head
        path.moveTo(width / 2 - 5, height * 3 / 4 - 5)
        path.lineTo(width / 2, height * 3 / 4)
        path.lineTo(width / 2 - 5, height * 3 / 4 + 5)
        # Add vertical line in the middle of the symbol
        path.moveTo(width / 2, 0)
        path.lineTo(width / 2, height)
        # Make sure the bounding rect is withing specifications
        path.moveTo(width, height)
        self.setPath(path)
        super(Label, self).set_shape(width, height)

    def parse_gr(self):
        ''' Return the PR string for a floating label (incl. transition) '''
        pos = self.scenePos()
        assert (not self.hasParent)
        result = ['/* CIF LABEL ({x}, {y}), ({w}, {h}) */\n'
                    '{hlink}'
                    'CONNECTION {label}:'.format(
                        label=str(self),
                        hlink=repr(self.text),
                        x=int(pos.x()), y=int(pos.y()),
                        w=int(self.boundingRect().width()),
                        h=int(self.boundingRect().height()))]
        # Recursively parse the branch
        next_symbol = self.next_aligned_symbol()
        while next_symbol:
            result.append(repr(next_symbol))
            next_symbol = next_symbol.next_aligned_symbol()
        result.append('/* CIF End Label */')
        result.append('ENDCONNECTION;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the PR string for a standard label '''
        pos = self.scenePos()
        return ('/* CIF LABEL ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{label}:'.format(label=str(self), hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


# pylint: disable=R0904
class Task(VerticalSymbol, object):
    ''' TASK symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'task'
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ''' Initializes the TASK symbol '''
        ast = ast or ogAST.Task()
        super(Task, self).__init__(parent, text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)

        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.lineTo(width, 0)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.lineTo(0, 0)
        self.setPath(path)
        super(Task, self).set_shape(width, height)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        return ('/* CIF TASK ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'TASK {t}{comment}'.format(t=str(self.text),
                    hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


# pylint: disable=R0904
class ProcedureCall(VerticalSymbol, object):
    ''' PROCEDURE CALL symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    common_name = 'procedure_call'
    # Define reserved keywords for the syntax highlighter
    blackbold = ['\\bWRITELN\\b', '\\bWRITE\\b',
                 '\\bSET_TIMER\\b', '\\bRESET_TIMER\\b']
    redbold = SDL_REDBOLD
    completion_list = {'set_timer', 'reset_timer', 'write', 'writeln'}

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output(defName='callMe')
        super(ProcedureCall, self).__init__(parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminal_symbol = False
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRect(0, 0, width, height)
        path.moveTo(7, 0)
        path.lineTo(7, height)
        path.moveTo(width - 7, 0)
        path.lineTo(width - 7, height)
        self.setPath(path)
        super(ProcedureCall, self).set_shape(width, height)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        return ('/* CIF PROCEDURECALL ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'CALL {p}{comment}'.format(p=str(self.text),
                    hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


# pylint: disable=R0904
class TextSymbol(HorizontalSymbol, object):
    ''' Text symbol - used to declare variables, etc. '''
    common_name = 'text_area'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, ast=None):
        ''' Create a Text Symbol '''
        ast = ast or ogAST.TextArea()
        super(TextSymbol, self).__init__(parent=None,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(249, 249, 249)))
        self.terminal_symbol = False
        self.setPos(ast.pos_x, ast.pos_y)
        # Disable hyperlinks for Text symbols
        self._no_hyperlink = True
        # Text is not centered in the box - change default alignment:
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.parser = ogParser

    def update_completion_list(self):
        ''' When text was entered, update TASK completion list '''
        # Get AST for the symbol
        ast, _, ___, ____, _____ = self.parser.parseSingleElement(
                    'text_area', repr(self))
        Task.completion_list |= {dcl for dcl in ast.variables.keys()}

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def set_shape(self, width, height):
        ''' Define the polygon of the text symbol '''
        path = QPainterPath()
        path.moveTo(width - 10, 0)
        path.lineTo(0, 0)
        path.lineTo(0, height)
        path.lineTo(width, height)
        path.lineTo(width, 10)
        path.lineTo(width - 10, 10)
        path.lineTo(width - 10, 0)
        path.lineTo(width, 10)
        self.setPath(path)
        super(TextSymbol, self).set_shape(width, height)

    def resize_item(self, rect):
        ''' Text Symbol only resizes down or right '''
        if self.grabber.resize_mode.endswith('left'):
            return
        self.prepareGeometryChange()
        self.set_shape(rect.width(), rect.height())

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        pos = self.scenePos()
        return ('/* CIF TEXT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{text}\n'
                '/* CIF ENDTEXT */'.format(text=str(self.text),
                    hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


class ASN1Viewer(TextSymbol):
    ''' Text symbol with dedicated text highlighting set of words for ASN.1 '''
    blackbold = ['\\b{}\\b'.format(word) for word in (
                 'DEFINITIONS', 'AUTOMATIC', 'TAGS', 'BEGIN', 'END', 'INTEGER',
                 'OCTET', 'STRING', 'BIT', 'REAL', 'SEQUENCE', 'OF', 'WITH',
                 'IMPORTS', 'FROM', 'SIZE', 'CHOICE', 'BOOLEAN')]


# pylint: disable=R0904
class State(VerticalSymbol, object):
    ''' SDL STATE Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = ['Input']
    arrow_head = True
    common_name = 'terminator_statement'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.State()
        # Note: ast coordinates are in scene coordinates
        super(State, self).__init__(parent=parent,
                text=ast.inputString, x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        self.terminal_symbol = True
        if parent:
            try:
                # Map AST scene coordinates to get actual position
                self.setPos(self.pos() 
                        + self.mapFromScene(ast.pos_x, ast.pos_y))
            except TypeError:
                self.update_position()
        else:
            # Use scene coordinates to position
            self.setPos(ast.pos_x, ast.pos_y)
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def update_completion_list(self):
        ''' When text was entered, update state completion list '''
        # Get AST for the symbol
        ast, _, ___, ____, _____ = self.parser.parseSingleElement(
                    'state', self.parse_gr(recursive=False))
        State.completion_list |= set(ast.statelist)

    def check_syntax(self):
        ''' Redefined function, to distinguish STATE and NEXTSTATE '''
        if self.hasParent:
            super(State, self).check_syntax()
        else:
            _, syntax_err, ___, ____, _____ = self.parser.parseSingleElement(
                    'state', self.parse_gr(recursive=False))
            try:
                self.scene().raise_syntax_errors(syntax_err)
            except:
                LOG.debug('raise_syntax_error raised an exception')

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 15, 50)
        self.setPath(path)
        super(State, self).set_shape(width, height)

    def get_ast(self):
        ''' Redefinition of the get_ast function for the state '''
        if self.hasParent and not [c for c in self.childSymbols()
                if not isinstance(c, Comment)]:
            # Terminator case
            return super(State, self).get_ast()
        else:
            # State case
            ast, _, ___, ____, terminators = self.parser.parseSingleElement(
                'state', self.parse_gr(recursive=True))
            return ast, terminators

    def parse_gr(self, recursive=True):
        ''' Parse state '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        if self.hasParent and not [s for s in self.childSymbols() if
                                   not isinstance(s, Comment)]:
            # Do not generate a new STATE when there is no need
            # FIXME: check if childSymbol is a commment
            return ''
        result = ['/* CIF STATE ({x}, {y}), ({w}, {h}) */\n'
                    '{hlink}'
                    'STATE {state}{comment}'.format(
                        state=str(self),
                        hlink=repr(self.text),
                        x=int(pos.x()), y=int(pos.y()),
                        w=int(self.boundingRect().width()),
                        h=int(self.boundingRect().height()), comment=comment)]
        if recursive:
            for i in self.childSymbols():
                # Recursively return next symbols (inputs)
                if isinstance(i, Input):
                    result.append(repr(i))
        result.append('ENDSTATE;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        result = ['/* CIF NEXTSTATE ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'NEXTSTATE {state}{comment}'.format(
                    state=str(self),
                    hlink=repr(self.text),
                    x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment)]
        return '\n'.join(result)


class Procedure(HorizontalSymbol, object):
    ''' Procedure declaration symbol '''
    _unique_followers = ['Comment']
    common_name = 'procedure'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD
    completion_list = set()

    def __init__(self, ast=None, subscene=None):
        ast = ast or ogAST.Procedure()
        super(Procedure, self).__init__(parent=None,
                text=ast.inputString,
                x=ast.pos_x, y=ast.pos_y, hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)
        self.nested_scene = subscene

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRect(10, 0, width-20, height)
        path.moveTo(10, 0)
        path.lineTo(0, 10)
        path.lineTo(0, height - 10)
        path.lineTo(10, height)
        path.moveTo(width - 10, 0)
        path.lineTo(width, 10)
        path.lineTo(width, height - 10)
        path.lineTo(width - 10, height)
        self.setPath(path)
        super(Procedure, self).set_shape(width, height)

    def update_completion_list(self):
        ''' When text was entered, update completion list of ProcedureCall '''
        ProcedureCall.completion_list |= {str(self.text)}

    def parse_gr(self, recursive=True):
        ''' Generate PR for a procedure '''
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        result = ['/* CIF PROCEDURE ({x}, {y}), ({w}, {h}) */\n'
                    '{hlink}'
                    'PROCEDURE {state}{comment}'.format(
                        state=str(self),
                        hlink=repr(self.text),
                        x=int(pos.x()), y=int(pos.y()),
                        w=int(self.boundingRect().width()),
                        h=int(self.boundingRect().height()), comment=comment)]
        if recursive:
            pr_raw = self.nested_scene.get_pr_string()
            # Keep only the body - it is not a PROCESS
            pr_data = pr_raw[1:-1]
            result.extend(pr_data)
        result.append('ENDPROCEDURE;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the complete procedure branch in PR format '''
        return self.parse_gr(recursive=True)



# pylint: disable=R0904
class Start(HorizontalSymbol, object):
    ''' SDL START Symbol '''
    _unique_followers = ['Comment']
    _insertable_followers = [
            'Task', 'ProcedureCall', 'Output', 'Decision', 'Label']
    _terminal_followers = ['Join', 'State', 'ProcedureStop']
    # There cannot be more than one START symbol in a scene
    is_singleton = True
    common_name = 'start'
    needs_parent = False
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def __init__(self, ast=None):
        ''' Create the START symbol '''
        ast = ast or ogAST.Start()
        self.terminal_symbol = False
        super(Start, self).__init__(parent=None, text='',
                x=ast.pos_x, y=ast.pos_y,
                hyperlink=ast.hyperlink)
        self.set_shape(ast.width, ast.height)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        # No hyperlink for START symbol because it has no text
        self._no_hyperlink = True
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' User cannot enter text in the START symbol - Return dummy text '''
        return 'START'

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 25, 25)
        self.setPath(path)
        super(Start, self).set_shape(width, height)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        result = []
        comment = repr(self.comment) if self.comment else ';'
        pos = self.scenePos()
        result.append('/* CIF START ({x}, {y}), ({w}, {h}) */\n'
                'START{comment}'.format(x=int(pos.x()), y=int(pos.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))
        # Recursively return the complete branch below the start symbol
        next_symbol = self.next_aligned_symbol()
        while next_symbol:
            result.append(repr(next_symbol))
            next_symbol = next_symbol.next_aligned_symbol()
        return '\n'.join(result)


class ProcedureStart(Start, object):
    ''' Start symbol of a procedure - only shape differs from Start '''
    # Define reserved keywords for the syntax highlighter
    blackbold = SDL_BLACKBOLD
    redbold = SDL_REDBOLD

    def set_shape(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 25, 25)
        path.moveTo(25, 0)
        path.lineTo(25, height)
        path.moveTo(width-25, 0)
        path.lineTo(width-25, height)
        self.setPath(path)
        super(Start, self).set_shape(width, height)
