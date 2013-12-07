#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int

    This module is managing the Copy and Paste functions.
"""

import ogAST
import sdlSymbols
import genericSymbols
import logging
import Renderer
import PySide

__all__ = ['copy', 'paste']

LOG = logging.getLogger(__name__)

# Buffer holding the list of copied symbols in AST form
COPY_PASTE = []

# Actual scene clipboard
CLIPBOARD = None

def copy(selection):
    ''' Create a copy (duplicate) of the selected symbols in AST form '''
    # Clear the copy paste buffer
    COPY_PASTE[:] = []
    branch_top_level = []
    floating_items = []
    for item in selection:
        # When several items are selected, take the first of each subbranch
        if item.hasParent and not item.parentItem().grabber.isSelected():
            branch_top_level.append(item)
        elif not item.hasParent and not item.is_singleton:
            # Take also floating items, if they allow for copy (e.g. not START)
            floating_items.append(item)
    # Check if selected items would allow a paste - reject copy otherwise
    # e.g. floating and non-floating items cannot be pasted together
    if ((branch_top_level == []) == (floating_items == []) or
            len(branch_top_level) > 1):
        raise TypeError('Selection is incompatible with copy')
    # Then parse/copy the selected branches
    for item in branch_top_level + floating_items:
        branch_ast, terminators = copy_branch(item)
        COPY_PASTE.append((branch_ast, terminators))
    LOG.debug('COPY-PASTE LIST:' + str(COPY_PASTE))


def copy_branch(top_level_item):
    ''' Copy branches (recursively) '''
    res_terminators = []
    item_ast, terminators = top_level_item.get_ast()
    LOG.debug('COPY ' + str(item_ast))

    # Set absolute (scene) coordinates of top level item
    scene_pos = top_level_item.scenePos()
    item_ast.abs_x = scene_pos.x()
    item_ast.abs_y = scene_pos.y()

    branch = [item_ast]

    # If top_level_item is an horizontal symbol, all its children (branch)
    # are automatically copied. In the case that several following symbols
    # are selected however, the followers of the top_level must be
    # explicitely added to the copy list:
    if not isinstance(top_level_item, genericSymbols.HorizontalSymbol):
        next_aligned = top_level_item.next_aligned_symbol()
        while next_aligned and next_aligned.grabber.isSelected():
            next_ast, next_terminators = next_aligned.get_ast()
            terminators.extend(next_terminators)
            branch.append(next_ast)
            next_aligned = next_aligned.next_aligned_symbol()

    # Parse terminators recursively (e.g. NEXTSTATE)
    res_terminators = terminators
    for term in terminators:
        # Get symbol at terminator coordinates
        symbols = top_level_item.scene().items(PySide.QtCore.QRectF
                (term.pos_x, term.pos_y, term.width, term.height).center())
        for symbol in symbols:
            if (isinstance(symbol, sdlSymbols.State) and [c for c in
                symbol.childSymbols() if isinstance(c, sdlSymbols.Input)]):
                term_branch, term_inators = copy_branch(symbol)
                branch.extend(term_branch)
                res_terminators.extend(term_inators)
    return branch, res_terminators

def paste(parent, scene):
    '''
        Paste previously copied symbols at selection point
    '''
    CLIPBOARD.clear()
    if not parent:
        new_symbols = paste_floating_objects(scene)
    else:
        new_symbols = paste_below_item(parent, scene)
    return new_symbols


def paste_floating_objects(scene):
    ''' Paste items with no parents (states, text areas) '''
    symbols = set()
    LOG.debug('PASTING FLOATING OBJECTS')

    for item_list, terminators in COPY_PASTE:
        # states is a list passed as parameter - not a generator:
        states = [i for i in item_list if isinstance(i, ogAST.State)]
        text_areas = (i for i in item_list if
                isinstance(i, ogAST.TextArea))
        for state in states:
            # First check if state has already been pasted
            try:
                new_item = Renderer.render(state, scene=CLIPBOARD,
                           terminators=terminators, states=states)
            except TypeError:
                # Discard terminators (explanation given in Renderer._state)
                pass
            else:
                LOG.debug('PASTE STATE "' + state.inputString + '"')
                symbols.add(new_item)
                # Insert the new state at click coordinates
                scene.addItem(new_item)
        for text_area in text_areas:
            LOG.debug('PASTE TEXT AREA')
            new_item = Renderer.render(text_area, scene)
            symbols.add(new_item)
    return symbols


def paste_below_item(parent, scene):
    ''' Paste items under a selected symbol '''
    LOG.debug('Pasting below item ' + repr(parent))
    symbols = set()
    for item_list, _ in COPY_PASTE:
        states = [i for i in item_list if isinstance(i, ogAST.State)]
        for i in [c for c in item_list if not isinstance
                (c, (ogAST.State, ogAST.TextArea, ogAST.Start))]:
            LOG.debug('PASTE ' + str(i))
            # Create the new item from the AST description
            new_item = Renderer.render(i, scene=CLIPBOARD,
                                       parent=None, states=states)
            # Check that item is compatible with parent
            if (type(new_item).__name__ in parent.allowed_followers):
                # Move the item from the clipboard to the scene
                scene.addItem(new_item)
                new_item.setPos(0, 0)
                symbols.add(new_item)
            else:
                raise TypeError('Cannot paste here ({t1} cannot follow {t2}'
                                .format(t1=type(new_item), t2=type(parent)))
    return symbols
