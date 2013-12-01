#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque

from atom.api import Bool, List, Callable, Value, Typed

from casuarius import weak

from enaml.layout.layout_helpers import expand_constraints
from enaml.layout.layout_manager import LayoutManager
from enaml.widgets.container import ProxyContainer

from .QtCore import QSize, Signal
from .QtGui import QFrame

from .qt_constraints_widget import QtConstraintsWidget, size_hint_guard
from .qt_frame import QtFrame


class QContainer(QFrame):
    """ A subclass of QFrame which behaves as a container.

    """
    #: A signal which is emitted on a resize event.
    resized = Signal()

    #: The internally cached size hint.
    _size_hint = QSize()

    def resizeEvent(self, event):
        """ Converts a resize event into a signal.

        """
        super(QContainer, self).resizeEvent(event)
        self.resized.emit()

    def sizeHint(self):
        """ Returns the previously set size hint. If that size hint is
        invalid, the superclass' sizeHint will be used.

        """
        hint = self._size_hint
        if not hint.isValid():
            hint = super(QContainer, self).sizeHint()
        return QSize(hint)

    def setSizeHint(self, hint):
        """ Sets the size hint to use for this widget.

        """
        self._size_hint = QSize(hint)

    def minimumSizeHint(self):
        """ Returns the minimum size hint for the widget.

        For a QContainer, the minimum size hint is equivalent to the
        minimum size as computed by the layout manager.

        """
        return self.minimumSize()


def hard_constraints(d):
    """ Generate hard constraints for an item.

    These constraints will always be included for an item in a layout.

    """
    return [d.left >= 0, d.top >= 0, d.width >= 0, d.height >= 0]


def can_shrink_in_width(d):
    """ Get whether a declarative container can shrink in width.

    """
    shrink = ('ignore', 'weak')
    return d.resist_width in shrink and d.hug_width in shrink


def can_shrink_in_height(d):
    """ Get whether a declarative container can shrink in height.

    """
    shrink = ('ignore', 'weak')
    return d.resist_height in shrink and d.hug_height in shrink


def can_expand_in_width(d):
    """ Get whether a declarative container can expand in width.

    """
    expand = ('ignore', 'weak')
    return d.hug_width in expand and d.limit_width in expand


def can_expand_in_height(d):
    """ Get whether a declarative container can expand in height.

    """
    expand = ('ignore', 'weak')
    return d.hug_height in expand and d.limit_height in expand


class QtContainer(QtFrame, ProxyContainer):
    """ A Qt implementation of an Enaml ProxyContainer.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QContainer)

    #: A list of the contents constraints for the widget.
    contents_cns = List()

    #: Whether or not this container owns its layout. A container which
    #: does not own its layout is not responsible for laying out its
    #: children on a resize event, and will proxy the call to its owner.
    _owns_layout = Bool(True)

    #: The object which has taken ownership of the layout for this
    #: container, if any.
    _layout_owner = Value()

    #: The LayoutManager instance to use for solving the layout system
    #: for this container.
    _layout_manager = Value()

    #: The function to use for refreshing the layout on a resize event.
    _refresh = Callable(lambda *args, **kwargs: None)

    #: The table of offsets to use during a layout pass.
    _offset_table = List()

    #: The table of (index, updater) pairs to use during a layout pass.
    _layout_table = List()

    def _default_contents_cns(self):
        """ Create the contents constraints for the container.

        The contents contraints are generated by combining the user
        padding with the margins returned by 'contents_margins' method.

        Returns
        -------
        result : list
            The list of casuarius constraints for the content.

        """
        d = self.declaration
        margins = self.contents_margins()
        top, right, bottom, left = map(sum, zip(d.padding, margins))
        cns = [
            d.contents_top == (d.top + top),
            d.contents_left == (d.left + left),
            d.contents_right == (d.left + d.width - right),
            d.contents_bottom == (d.top + d.height - bottom),
        ]
        return cns

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the QContainer widget.

        """
        self.widget = QContainer(self.parent_widget())

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtContainer, self).init_widget()
        self.widget.resized.connect(self.on_resized)

    def init_layout(self):
        """ Initialize the layout of the widget.

        """
        super(QtContainer, self).init_layout()
        self.init_cns_layout()

    def init_cns_layout(self):
        """ Initialize the constraints layout.

        """
        # Layout ownership can only be transferred *after* this init
        # layout method is called, since layout occurs bottom up. So,
        # we only initialize a layout manager if ownership is unlikely
        # to be transferred.
        if not self.will_transfer():
            offset_table, layout_table = self._build_layout_table()
            cns = self._generate_constraints(layout_table)
            manager = LayoutManager()
            manager.initialize(cns)
            self._offset_table = offset_table
            self._layout_table = layout_table
            self._layout_manager = manager
            self._refresh = self._build_refresher(manager)
            self._update_sizes()

    def destroy(self):
        """ An overridden destructor method.

        This method breaks the internal reference cycles maintained
        by the container.

        """
        del self._layout_table
        del self._refresh
        super(QtContainer, self).destroy()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event.

        This handler will reparent the child if necessary.

        """
        super(QtContainer, self).child_added(child)
        cw = child.widget
        if cw is not None and cw.parent() != self.widget:
            cw.setParent(self.widget)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_resized(self):
        """ Update the position of the widgets in the layout.

        This makes a layout pass over the descendents if this widget
        owns the responsibility for their layout.

        """
        # The _refresh function is generated on every relayout and has
        # already taken into account whether or not the container owns
        # the layout.
        self._refresh()

    #--------------------------------------------------------------------------
    # ProxyConstraintsWidget API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ A reimplemented layout request handler.

        This method drops the references to layout tables and layout
        refresh function. This prevents edge case scenarios where a parent
        container layout will occur before a child container, causing the
        child to resize (potentially) deleted widgets still held as refs
        in the layout table.

        """
        super(QtContainer, self).request_relayout()
        del self._layout_table
        del self._offset_table
        del self._refresh

    #--------------------------------------------------------------------------
    # Public Layout Handling
    #--------------------------------------------------------------------------
    def relayout(self):
        """ Rebuild the constraints layout for the widget.

        If this object does not own the layout, the call is proxied to
        the layout owner.

        """
        if self._owns_layout:
            with size_hint_guard(self):
                self.init_cns_layout()
                self._refresh()
        else:
            self._layout_owner.relayout()

    def replace_constraints(self, old_cns, new_cns):
        """ Replace constraints in the given layout.

        This method can be used to selectively add/remove/replace
        constraints in the layout system, when it is more efficient
        than performing a full relayout.

        Parameters
        ----------
        old_cns : list
            The list of casuarius constraints to remove from the
            the current layout system.

        new_cns : list
            The list of casuarius constraints to add to the
            current layout system.

        """
        if self._owns_layout:
            manager = self._layout_manager
            if manager is not None:
                with size_hint_guard(self):
                    manager.replace_constraints(old_cns, new_cns)
                    self._update_sizes()
                    self._refresh()
        else:
            self._layout_owner.replace_constraints(old_cns, new_cns)

    def contents_margins(self):
        """ Get the contents margins for the container.

        The contents margins are added to the user provided padding
        to determine the final offset from a layout box boundary to
        the corresponding content line. The default content margins
        are zero. This method can be reimplemented by subclasses to
        supply different margins.

        Returns
        -------
        result : tuple
            A tuple of 'top', 'right', 'bottom', 'left' contents
            margins to use for computing the contents constraints.

        """
        return (0, 0, 0, 0)

    def contents_margins_updated(self):
        """ Notify the system that the contents margins have changed.

        """
        old_cns = self.contents_cns
        del self.contents_cns
        new_cns = self.contents_cns
        self.replace_constraints(old_cns, new_cns)

    #--------------------------------------------------------------------------
    # Private Layout Handling
    #--------------------------------------------------------------------------
    def _layout(self):
        """ The layout callback invoked by the layout manager.

        This iterates over the layout table and calls the geometry
        updater functions.

        """
        # We explicitly don't use enumerate() to generate the running
        # index because this method is on the code path of the resize
        # event and hence called *often*. The entire code path for a
        # resize event is micro optimized and justified with profiling.
        offset_table = self._offset_table
        layout_table = self._layout_table
        running_index = 1
        for offset_index, updater in layout_table:
            dx, dy = offset_table[offset_index]
            new_offset = updater(dx, dy)
            offset_table[running_index] = new_offset
            running_index += 1

    def _update_sizes(self):
        """ Update the min/max/best sizes for the underlying widget.

        This method is called automatically at the proper times. It
        should not normally need to be called by user code.

        """
        widget = self.widget
        widget.setSizeHint(self.compute_best_size())
        if not isinstance(widget.parent(), QContainer):
            # Only set min and max size if the parent is not a container.
            # The layout manager needs to be the ultimate authority when
            # dealing with nested containers.
            widget.setMinimumSize(self.compute_min_size())
            widget.setMaximumSize(self.compute_max_size())

    def _build_refresher(self, manager):
        """ Build the refresh function for the container.

        Parameters
        ----------
        manager : LayoutManager
            The layout manager to use when refreshing the layout.

        """
        # The return function is a hyper optimized (for Python) closure
        # in order minimize the amount of work which is performed on the
        # code path of the resize event. This is explicitly not idiomatic
        # Python code. It exists purely for the sake of efficiency,
        # justified with profiling.
        mgr_layout = manager.layout
        d = self.declaration
        layout = self._layout
        width_var = d.width
        height_var = d.height
        widget = self.widget
        width = widget.width
        height = widget.height
        return lambda: mgr_layout(layout, width_var, height_var, (width(), height()))

    def _build_layout_table(self):
        """ Build the layout table for this container.

        A layout table is a pair of flat lists which hold the required
        objects for laying out the child widgets of this container.
        The flat table is built in advance (and rebuilt if and when
        the tree structure changes) so that it's not necessary to
        perform an expensive tree traversal to layout the children
        on every resize event.

        Returns
        -------
        result : (list, list)
            The offset table and layout table to use during a resize
            event.

        """
        # The offset table is a list of (dx, dy) tuples which are the
        # x, y offsets of children expressed in the coordinates of the
        # layout owner container. This owner container may be different
        # from the parent of the widget, and so the delta offset must
        # be subtracted from the computed geometry values during layout.
        # The offset table is updated during a layout pass in breadth
        # first order.
        #
        # The layout table is a flat list of (idx, updater) tuples. The
        # idx is an index into the offset table where the given child
        # can find the offset to use for its layout. The updater is a
        # callable provided by the widget which accepts the dx, dy
        # offset and will update the layout geometry of the widget.
        zero_offset = (0, 0)
        offset_table = [zero_offset]
        layout_table = []
        queue = deque((0, child) for child in self.children())

        # Micro-optimization: pre-fetch bound methods and store globals
        # as locals. This method is not on the code path of a resize
        # event, but it is on the code path of a relayout. If there
        # are many children, the queue could potentially grow large.
        push_offset = offset_table.append
        push_item = layout_table.append
        push = queue.append
        pop = queue.popleft
        QtConstraintsWidget_ = QtConstraintsWidget
        QtContainer_ = QtContainer
        isinst = isinstance

        # The queue yields the items in the tree in breadth-first order
        # starting with the immediate children of this container. If a
        # given child is a container that will share its layout, then
        # the children of that container are added to the queue to be
        # added to the layout table.
        running_index = 0
        while queue:
            offset_index, item = pop()
            if isinst(item, QtConstraintsWidget_):
                push_item((offset_index, item.geometry_updater()))
                push_offset(zero_offset)
                running_index += 1
                if isinst(item, QtContainer_):
                    if item.transfer_layout_ownership(self):
                        for child in item.children():
                            push((running_index, child))

        return offset_table, layout_table

    def _generate_constraints(self, layout_table):
        """ Creates the list of casuarius LinearConstraint objects for
        the widgets for which this container owns the layout.

        This method walks over the items in the given layout table and
        aggregates their constraints into a single list of casuarius
        LinearConstraint objects which can be given to the layout
        manager.

        Parameters
        ----------
        layout_table : list
            The layout table created by a call to _build_layout_table.

        Returns
        -------
        result : list
            The list of casuarius LinearConstraints instances to pass to
            the layout manager.

        """
        # The list of raw casuarius constraints which will be returned
        # from this method to be added to the casuarius solver.
        cns = self.contents_cns[:]
        d = self.declaration
        cns.extend(hard_constraints(d))
        cns.extend(expand_constraints(d, d.layout_constraints()))

        # The first element in a layout table item is its offset index
        # which is not relevant to constraints generation. The child
        # size hint constraints are refreshed unconditionally. This
        # accounts for the potential changes in the size hint of a
        # widget between relayouts.
        for _, updater in layout_table:
            child = updater.item
            del child.size_hint_cns
            d = child.declaration
            cns.extend(hard_constraints(d))
            if isinstance(child, QtContainer):
                if child.transfer_layout_ownership(self):
                    cns.extend(expand_constraints(d, d.layout_constraints()))
                    cns.extend(child.contents_cns)
                else:
                    cns.extend(child.size_hint_cns)
            else:
                cns.extend(expand_constraints(d, d.layout_constraints()))
                cns.extend(child.size_hint_cns)

        return cns

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def transfer_layout_ownership(self, owner):
        """ A method which can be called by other components in the
        hierarchy to gain ownership responsibility for the layout
        of the children of this container. By default, the transfer
        is allowed and is the mechanism which allows constraints to
        cross widget boundaries. Subclasses should reimplement this
        method if different behavior is desired.

        Parameters
        ----------
        owner : Declarative
            The component which has taken ownership responsibility
            for laying out the children of this component. All
            relayout and refresh requests will be forwarded to this
            component.

        Returns
        -------
        results : bool
            True if the transfer was allowed, False otherwise.

        """
        if not self.declaration.share_layout:
            return False
        self._owns_layout = False
        self._layout_owner = owner
        del self._layout_manager
        del self._refresh
        del self._offset_table
        del self._layout_table
        return True

    def will_transfer(self):
        """ Whether or not the container expects to transfer its layout
        ownership to its parent.

        This method is predictive in nature and exists so that layout
        managers are not senslessly created during the bottom-up layout
        initialization pass. It is declared public so that subclasses
        can override the behavior if necessary.

        """
        d = self.declaration
        return d.share_layout and isinstance(self.parent(), QtContainer)

    def compute_min_size(self):
        """ Calculates the minimum size of the container which would
        allow all constraints to be satisfied.

        If the container's resist properties have a strength less than
        'medium', the returned size will be zero. If the container does
        not own its layout, the returned size will be invalid.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the minimum size
            required to satisfy all constraints.

        """
        d = self.declaration
        shrink_w = can_shrink_in_width(d)
        shrink_h = can_shrink_in_height(d)
        if shrink_w and shrink_h:
            return QSize(0, 0)
        if self._owns_layout and self._layout_manager is not None:
            w, h = self._layout_manager.get_min_size(d.width, d.height)
            if shrink_w:
                w = 0
            if shrink_h:
                h = 0
            return QSize(w, h)
        return QSize()

    def compute_best_size(self):
        """ Calculates the best size of the container.

        The best size of the container is obtained by computing the min
        size of the layout using a strength which is much weaker than a
        normal resize. This takes into account the size of any widgets
        which have their resist clip property set to 'weak' while still
        allowing the window to be resized smaller by the user. If the
        container does not own its layout, the returned size will be
        invalid.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the best size that
            will satisfy all constraints.

        """
        if self._owns_layout and self._layout_manager is not None:
            d = self.declaration
            w, h = self._layout_manager.get_min_size(d.width, d.height, weak)
            return QSize(w, h)
        return QSize()

    def compute_max_size(self):
        """ Calculates the maximum size of the container which would
        allow all constraints to be satisfied.

        If the container's hug properties have a strength less than
        'medium', or if the container does not own its layout, the
        returned size will be the Qt maximum.

        Returns
        -------
        result : QSize
            A (potentially invalid) QSize which is the maximum size
            allowable while still satisfying all constraints.

        """
        d = self.declaration
        expand_w = can_expand_in_width(d)
        expand_h = can_expand_in_height(d)
        if expand_w and expand_h:
            return QSize(16777215, 16777215)
        if self._owns_layout and self._layout_manager is not None:
            w, h = self._layout_manager.get_max_size(d.width, d.height)
            if w < 0 or expand_w:
                w = 16777215
            if h < 0 or expand_h:
                h = 16777215
            return QSize(w, h)
        return QSize(16777215, 16777215)
