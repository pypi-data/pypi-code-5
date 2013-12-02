# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

import types

from pyxrd.generic.models import ChildModel, PropIntel, HoldableSignal
from pyxrd.generic.models.treemodels import ObjectListStore
from pyxrd.generic.models.metaclasses import pyxrd_object_pool
from pyxrd.generic.models.mixins import ObjectListStoreChildMixin
from pyxrd.generic.io import storables, Storable, get_case_insensitive_glob

from pyxrd.generic.refinement.mixins import RefinementValue

# from gtk import ListStore

class ComponentPropMixin(object):
    """
        A mixin which provides some common utility functions for retrieving
        properties using a string description (e.g. 'layer_atoms.1' or 'b_cell')
    """

    def __init__(self, *args, **kwargs):
        # Nothing to do but ignore any extraneous args & kwargs passed down
        super(ComponentPropMixin, self).__init__()

    def _parseattr(self, attr):
        """
            Function used for handling (deprecated) 'property strings':
            attr contains a string (e.g. cell_a or layer_atoms.2) which can be 
            parsed into an object and a property.
            Current implementation uses UUID's, however this is still here for
            backwards-compatibility...
            Will be removed at some point!
        """
        if not isinstance(attr, types.StringTypes):
            return attr

        if attr == "" or attr == None:
            return None

        attr = attr.replace("data_", "", 1) # for backwards compatibility
        attrs = attr.split(".")
        if attrs[0] == "layer_atoms":
            return self.component._layer_atoms._model_data[int(attrs[1])], "pn"
        elif attrs[0] == "interlayer_atoms":
            return self.component._interlayer_atoms._model_data[int(attrs[1])], "pn"
        else:
            return self.component, attr

@storables.register()
class AtomRelation(ChildModel, Storable, ObjectListStoreChildMixin, ComponentPropMixin, RefinementValue):

    # MODEL INTEL:
    __parent_alias__ = "component"
    __model_intel__ = [
        PropIntel(name="name", label="Name", data_type=unicode, is_column=True, storable=True, has_widget=True),
        PropIntel(name="value", label="Value", data_type=float, is_column=True, storable=True, has_widget=True, widget_type='float_entry', refinable=True),
        PropIntel(name="enabled", label="Enabled", data_type=bool, is_column=True, storable=True, has_widget=True),

        PropIntel(name="data_changed", data_type=object),
    ]
    __store_id__ = "AtomRelation"
    __file_filters__ = [
        ("Atom relation", get_case_insensitive_glob("*.atr")),
    ]
    allowed_relations = {}

    # SIGNALS:
    data_changed = None

    # PROPERTIES:
    _value = 0.0
    def get_value_value(self): return self._value
    def set_value_value(self, value):
        self._value = value
        self.data_changed.emit()
        self.liststore_item_changed()

    _name = ""
    def get_name_value(self): return self._name
    def set_name_value(self, value):
        self._name = value
        self.liststore_item_changed()

    _enabled = False
    def get_enabled_value(self): return self._enabled
    def set_enabled_value(self, value):
        self._enabled = value
        self.data_changed.emit()

    @property
    def applicable(self):
        """
        Is true when this AtomRelations was passed a component of which the atom
        ratios are not set to be inherited from another component.
        """
        return (self.parent is not None and not self.parent.inherit_atom_relations)

    # REFINEMENT VALUE IMPLEMENTATION:
    @property
    def refine_title(self):
        return self.name

    @property
    def refine_value(self):
        return self.value
    @refine_value.setter
    def refine_value(self, value):
        self.value = value

    @property
    def is_refinable(self):
        return self.enabled

    @property
    def refine_info(self):
        return self.value_ref_info

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """
            Valid keyword arguments for an AtomRelation are:
                name: the name of this AtomRelation
                value: the value for this AtomRelation
                enabled: boolean indicating whether or not this AtomRelation is 
                 enabled
        """
        super(AtomRelation, self).__init__(*args, **kwargs)

        self.data_changed = HoldableSignal()
        self.name = self.get_kwarg(kwargs, "", "name")
        self.value = self.get_kwarg(kwargs, "", "value")
        self.enabled = bool(self.get_kwarg(kwargs, True, "enabled"))

    # ------------------------------------------------------------
    #      Input/Output stuff
    # ------------------------------------------------------------
    def resolve_relations(self):
        raise NotImplementedError, "Subclasses should implement the resolve_relations method!"

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def create_prop_store(self, prop=None):
        if self.component is not None:
            import gtk
            store = gtk.ListStore(object, str, object)
            for atom in self.component._layer_atoms.iter_objects():
                store.append([atom, "pn", lambda o: o.name])
            for atom in self.component._interlayer_atoms.iter_objects():
                store.append([atom, "pn", lambda o: o.name])
            for relation in self.component._atom_relations.iter_objects():
                tp = relation.__store_id__
                if tp in self.allowed_relations:
                    prop, name = self.allowed_relations[tp]
                    store.append([relation, prop, name])
            return store

    def iter_references(self):
        raise NotImplementedError, "'iter_references' should be implemented by subclasses!"

    def _safe_is_referring(self, value):
        if value is not None and hasattr(value, "is_referring"):
            return value.is_referring([self, ])
        else:
            return False

    def is_referring(self, references=None):
        """
            Checks whether this AtomRelation is causing circular references.
            Can be used to check this before actually setting references by
            setting the 'references' keyword argument to a list containing the
            new reference value(s).
        """
        if references == None:
            references = []
        # 1. Bluntly check if we're not already somewhere referred to,
        #    if not, add ourselves to the list of references
        if self in references:
            return True
        references.append(self)

        # 2. Loop over our own references, check if they cause a circular
        #    reference, if not add them to the list of references.
        for reference in self.iter_references():
            if reference is not None and hasattr(reference, "is_referring"):
                if reference.is_referring(references):
                    return True
                else:
                    references.append(reference)

        return False

    def apply_relation(self):
        raise NotImplementedError, "Subclasses should implement the apply_relation method!"

    pass # end of class

@storables.register()
class AtomRatio(AtomRelation):

    # MODEL INTEL:
    __parent_alias__ = "component"
    __model_intel__ = [
        PropIntel(name="sum", label="Sum", data_type=float, widget_type='float_entry', is_column=True, storable=True, has_widget=True, minimum=0.0),
        PropIntel(name="atom1", label="Substituting Atom", data_type=object, is_column=True, storable=True, has_widget=True),
        PropIntel(name="atom2", label="Original Atom", data_type=object, is_column=True, storable=True, has_widget=True),
    ]
    __store_id__ = "AtomRatio"
    allowed_relations = {
        "AtomRatio": ("__internal_sum__", lambda o: o.name),
        "AtomContents": ("value", lambda o: o.name),
    }

    # SIGNALS:

    # PROPERTIES:
    _sum = 1.0
    def get_sum_value(self): return self._sum
    def set_sum_value(self, value):
        self._sum = float(value)
        self.data_changed.emit()

    def __internal_sum__(self, value):
        """
            Special setter for other AtomRelation objects depending on the value
            of the sum of the AtomRatio. This can be used to have multi-substitution
            by linking two (or more) AtomRatio's. Eg Al-by-Mg-&-Fe:
            AtomRatioMgAndFeForAl -> links together Al content and Fe+Mg content => sum = e.g. 4
            AtomRatioMgForFe -> links together the Fe and Mg content => sum = set by previous ratio.
        """
        self._sum = float(value)
        self.apply_relation()
    __internal_sum__ = property(fset=__internal_sum__)

    _atom1 = [None, None]
    def get_atom1_value(self): return self._atom1
    def set_atom1_value(self, value):
        with self.data_changed.hold():
            if not self._safe_is_referring(value[0]):
                self._atom1 = value
                self.data_changed.emit()

    _atom2 = [None, None]
    def get_atom2_value(self): return self._atom2
    def set_atom2_value(self, value):
        with self.data_changed.hold():
            if not self._safe_is_referring(value[0]):
                self._atom2 = value
                self.data_changed.emit()

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, *args, **kwargs): # @ReservedAssignment
        """
            Valid keyword arguments for an AtomRatio are:
                sum: the sum of the atoms contents
                atom1: a tuple containing the first atom and its property name to read/set
                atom2: a tuple containing the first atom and its property name to read/set
            The value property is the 'ratio' of the first atom over the sum of both
        """
        super(AtomRatio, self).__init__(*args, **kwargs)

        self.sum = self.get_kwarg(kwargs, self.sum, "sum", "data_sum")

        self._unresolved_atom1 = self._parseattr(self.get_kwarg(kwargs, [None, None], "atom1", "prop1", "data_prop1"))
        self._unresolved_atom2 = self._parseattr(self.get_kwarg(kwargs, [None, None], "atom2", "prop2", "data_prop2"))

    # ------------------------------------------------------------
    #      Input/Output stuff
    # ------------------------------------------------------------
    def json_properties(self):
        retval = Storable.json_properties(self)
        retval["atom1"] = [retval["atom1"][0].uuid if retval["atom1"][0] else None, retval["atom1"][1]]
        retval["atom2"] = [retval["atom2"][0].uuid if retval["atom2"][0] else None, retval["atom2"][1]]
        return retval

    def resolve_relations(self):
        if isinstance(self._unresolved_atom1[0], basestring):
            self._unresolved_atom1[0] = pyxrd_object_pool.get_object(self._unresolved_atom1[0])
        self.atom1 = list(self._unresolved_atom1)
        del self._unresolved_atom1
        if isinstance(self._unresolved_atom2[0], basestring):
            self._unresolved_atom2[0] = pyxrd_object_pool.get_object(self._unresolved_atom2[0])
        self.atom2 = list(self._unresolved_atom2)
        del self._unresolved_atom2

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def apply_relation(self):
        if self.enabled and self.applicable:
            for value, (atom, prop) in [(self.value, self.atom1), (1.0 - self.value, self.atom2)]:
                if atom and prop:
                    # do not fire events, just set attributes:
                    with atom.data_changed.ignore():
                        setattr(atom, prop, value * self.sum)

    def iter_references(self):
        for atom in [self.atom1[0], self.atom2[0]]:
            yield atom

    pass # end of class


class AtomContentObject(object):
    """
        Wrapper around an atom object used in the AtomContents model.
        Stores the atom, the property to set and it's default amount.
    """
    __columns__ = [
        ("atom", object),
        ("prop", object),
        ("amount", float)
    ]

    def __init__(self, atom, prop, amount, **kwargs):
        super(AtomContentObject, self).__init__()
        self.atom = atom
        self.prop = prop
        self.amount = amount

    def update_atom(self, value):
        if not (self.atom == "" or self.atom == None or self.prop == None):
            setattr(self.atom, self.prop, self.amount * value);

    pass

@storables.register()
class AtomContents(AtomRelation):

    # MODEL INTEL:
    __parent_alias__ = "component"
    __model_intel__ = [
        PropIntel(name="atom_contents", label="Atom contents", data_type=object, is_column=True, storable=True, has_widget=True),
    ]
    __store_id__ = "AtomContents"

    allowed_relations = {
        "AtomRatio": ("__internal_sum__", lambda o: o.name),
    }

    # SIGNALS:

    # PROPERTIES:
    _atom_contents = None
    def get_atom_contents_value(self): return self._atom_contents

    # ------------------------------------------------------------
    #      Initialisation and other internals
    # ------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """
            Valid keyword arguments for an AtomContents are:
                atom_contents: a list of tuples containing the atom content 
                 object uuids, property names and default amounts 
        """
        super(AtomContents, self).__init__(*args, **kwargs)

        self._atom_contents = ObjectListStore(AtomContentObject)
        atom_contents = self.get_kwarg(kwargs, None, "atom_contents")
        if atom_contents:
            # uuid's are resolved by calling resolve_relations
            for uuid, prop, amount in atom_contents:
                self._atom_contents.append(AtomContentObject(uuid, prop, amount))

        def on_change(*args):
            if self.enabled: # no need for updates in this case
                self.data_changed.emit()
        self._atom_contents.connect("row-changed", on_change)
        self._atom_contents.connect("row-inserted", on_change)
        self._atom_contents.connect("row-deleted", on_change)

    # ------------------------------------------------------------
    #      Input/Output stuff
    # ------------------------------------------------------------
    def json_properties(self):
        retval = Storable.json_properties(self)
        retval["atom_contents"] = list([
            [
                atom_contents.atom.uuid if atom_contents.atom else None,
                atom_contents.prop,
                atom_contents.amount
            ] for atom_contents in retval["atom_contents"].iter_objects()
        ])
        return retval

    def resolve_relations(self):
        # Disable event dispatching to prevent infinite loops
        enabled = self.enabled
        self.enabled = False
        # Change rows with string references to objects (uuid's)
        for atom_content in self.atom_contents.iter_objects():
            if isinstance(atom_content.atom, basestring):
                atom_content.atom = pyxrd_object_pool.get_object(atom_content.atom)
        # Set the flag to its original value
        self.enabled = enabled

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def apply_relation(self):
        if self.enabled and self.applicable:
            for atom_content in self.atom_contents.iter_objects():
                # do not fire events, just set attributes:
                if atom_content.atom is not None:
                    with atom_content.atom.data_changed.ignore():
                        atom_content.update_atom(self.value)

    def set_atom_content_values(self, path, new_atom, new_prop):
        """    
            Convenience function that first checks if the new atom value will
            not cause a circular reference before actually setting it.
        """
        with self.data_changed.hold():
            atom_content = self.atom_contents.get_item_by_index(int(path[0]))
            if atom_content.atom != new_atom:
                old_atom = atom_content.atom
                atom_content.atom = None # clear...
                if not self._safe_is_referring(new_atom):
                    atom_content.atom = new_atom
                else:
                    atom_content.atom = old_atom
            else:
                atom_content.atom = None
            atom_content.prop = new_prop

    def iter_references(self):
        for atom_content in self.atom_contents.iter_objects():
            yield atom_content.atom

    pass # end of class
