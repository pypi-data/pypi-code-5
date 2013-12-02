#  Author: Roberto Cavada <roboogle@gmail.com>
#
#  Copyright (c) 2005 by Roberto Cavada
#
#  pygtkmvc is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
#
#  pygtkmvc is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110, USA.
#
#  For more information on pygtkmvc see <http://pygtkmvc.sourceforge.net>
#  or email to the author Roberto Cavada <roboogle@gmail.com>.
#  Please report bugs to <roboogle@gmail.com>.

import types
import fnmatch

from pyxrd.gtkmvc.support import wrappers
from pyxrd.gtkmvc.support.log import logger

# ----------------------------------------------------------------------

OBS_TUPLE_NAME = "__observables__"

# old name, supported only for backward compatilibity, do not use it
# anymore in new code
PROPS_MAP_NAME = "__properties__"

# This keeps the names of all observable properties (old and new)
ALL_OBS_SET = "__all_observables__"

# name of the variable that hold a property value
PROP_NAME = "_prop_%(prop_name)s"

# these are the names of the internal maps associating logical
# properties names to their getters/setters
LOGICAL_GETTERS_MAP_NAME = "_getdict"
LOGICAL_SETTERS_MAP_NAME = "_setdict"

# WARNING! These variables and code using them is deprecated These are
# the names for property getter/setter methods that depend on property
# name
GET_PROP_NAME = "get_%(prop_name)s_value"
SET_PROP_NAME = "set_%(prop_name)s_value"

# There are the names for generic property getter/setter methods
GET_GENERIC_NAME = "get__value"
SET_GENERIC_NAME = "set__value"

# this used for pattern matching
WILDCARDS = frozenset("[]!*?")


class PropertyMeta (type):
    """This is a meta-class that provides auto-property support.
    The idea is to allow programmers to define some properties which
    will be automatically connected to auto-generated code which handles
    access to those properties.
    How can you use this meta-class?
    First, '__metaclass__ = PropertyMeta' must be class member of the class
    you want to make the automatic properties handling.
    Second, '__properties__' must be a map containing the properties names
    as keys, values will be initial values for properties.
    That's all: after the instantiation, your class will contain all properties
    you named inside '__properties__'. Each of them will be also associated
    to a couple of automatically-generated functions which get and set the
    property value inside a generated member variable.
    About names: suppose the property is called 'x'.  The generated variable
    (which keeps the real value of the property x) is called _prop_x.
    The getter is called get_prop_x(self), and the setter is called
    'set_prop_x(self, value)'.

    Customization:
    The base implementation of getter is to return the value stored in the
    variable associated to the property. The setter simply sets its value.
    Programmers can override basic behaviour for getters or setters simply by
    defining their getters and setters (see at the names convention above).
    The customized function can lie everywhere in the user classes hierarchy.
    Every overridden function will not be generated by the metaclass.

    To supply your own methods is good for few methods, but can result in a
    very unconfortable way for many methods. In this case you can extend
    the meta-class, and override methods get_[gs]etter_source with your
    implementation (this can be probably made better).
    An example is provided in meta-class PropertyMetaVerbose below.
    """

    def __init__(cls, name, bases, _dict):
        """class constructor"""
        type.__init__(cls, name, bases, _dict)

        # the set of all obs (it is calculated and stored below)
        obs = set()

        # processes now all names in __observables__
        conc_props, log_props = type(cls).__get_observables_sets__(cls)

        # processes all concrete properties
        for prop in conc_props:
            val = _dict[prop] # must exist if concrete
            type(cls).__create_conc_prop_accessors__(cls, prop, val)
            obs.add(prop)
            pass

        # processes all logical properties, and adds the actual log
        # properties to the list of all observables
        _getdict = getattr(cls, LOGICAL_GETTERS_MAP_NAME, dict())
        _setdict = getattr(cls, LOGICAL_SETTERS_MAP_NAME, dict())

        real_log_props = type(cls).__create_log_props(cls, log_props,
                                                      _getdict, _setdict)
        obs |= real_log_props

        # after using the maps, it is time to clear them to make
        # them available to the next class in the mro.
        _getdict.clear()
        _setdict.clear()

        # processes all names in __properties__ (deprecated,
        # overloaded by __observables__)
        props = getattr(cls, PROPS_MAP_NAME, {})
        if len(props) > 0:
            import warnings
            warnings.warn("In class %s.%s the use of attribute '%s' in "
                          "models is deprecated."
                          " Use the tuple '%s' instead (see the manual)" \
                              % (cls.__module__, cls.__name__,
                                 PROPS_MAP_NAME, OBS_TUPLE_NAME),
                          DeprecationWarning)
            pass
        for prop in (x for x in props.iterkeys() if x not in obs):
            type(cls).__create_conc_prop_accessors__(cls, prop, props[prop])
            obs.add(prop)
            pass

        # generates the list of _all_ properties available for this
        # class (also from bases)
        for base in bases: obs |= getattr(base, ALL_OBS_SET, set())
        setattr(cls, ALL_OBS_SET, frozenset(obs))
        logger.debug("class %s.%s has observables: %s" \
                         % (cls.__module__, cls.__name__, obs))
        return


    def __get_observables_sets__(cls):
        """Returns a pair of frozensets. First set of strings is the set
        of concrete properties, obtained by expanding wildcards
        found in class field __observables__. Expansion works only
        with names not prefixed with __.

        Second set of strings contains the names of the logical
        properties. This set may still contain logical properties
        which have not been associated with a getter (and
        optionally with a setter).
        """
        conc_prop_set = set()
        log_prop_set = set()

        not_found = []
        names = cls.__dict__.get(OBS_TUPLE_NAME, tuple())

        if not isinstance(names, types.ListType) and \
                not isinstance(names, types.TupleType):
            raise TypeError("In class %s.%s attribute '%s' must be a list or tuple" %
                            (cls.__module__, cls.__name__, OBS_TUPLE_NAME))

        for name in names:
            if type(name) != types.StringType:
                raise TypeError("In class %s.%s attribute '%s' must contain"\
                                    " only strings (found %s)" %
                                (cls.__module__, cls.__name__, OBS_TUPLE_NAME,
                                 type(name)))
            if (cls.__dict__.has_key(name) and not
                isinstance(getattr(cls, name), types.MethodType)):
                conc_prop_set.add(name)
            else: not_found.append(name)
            pass

        # now searches all possible matches for those that have not
        # been found, and collects all logical properties as well
        # (those which do not match, and do not contain patterns)
        concrete_members = [x for x, v in cls.__dict__.iteritems()
                            if (not x.startswith("__") and
                                not isinstance(v, types.FunctionType) and
                                not isinstance(v, types.MethodType) and
                                type(v) is not classmethod and
                                x not in conc_prop_set)]

        for pat in not_found:
            if frozenset(pat) & WILDCARDS:
                matches = fnmatch.filter(concrete_members, pat)
                if 0 == len(matches):
                    logger.warning("In class %s.%s observable pattern '%s' " \
                                       "did not match any existing attribute." % \
                                       (cls.__module__, cls.__name__, pat))
                else: conc_prop_set |= set(matches)
            else: # here pat has to be a logical property
                log_prop_set.add(pat)
                pass

            pass

        return (frozenset(conc_prop_set), frozenset(log_prop_set))


    def __create_log_props(cls, log_props, _getdict, _setdict):
        """Creates all the logical property. 

        The list of names of properties to be created is passed
        with frozenset log_props. The getter/setter information is
        taken from _{get,set}dict.

        This method resolves also wildcards in names, and performs
        all checks to ensure correctness.

        Returns the frozen set of the actually created properties
        (as not log_props may be really created, e.g. when no
        getter is provided, and a warning is issued).
        """

        real_log_props = set()
        resolved_getdict = {}
        resolved_setdict = {}

        for _dict_name, _dict, _resolved_dict in (("getter",
                                                   _getdict, resolved_getdict),
                                                  ("setter",
                                                   _setdict, resolved_setdict)):
            # first resolve all wildcards
            for pat, ai in ((pat, ai)
                            for pat, ai in _dict.iteritems()
                            if frozenset(pat) & WILDCARDS):
                matches = fnmatch.filter(log_props, pat)
                for match in matches:
                    if match in _resolved_dict:
                        raise NameError("In class %s.%s %s property '%s' "
                                        "is matched multiple times by patterns" % \
                                        (cls.__module__, cls.__name__, _dict_name, match))
                    _resolved_dict[match] = ai
                    pass

                if not matches:
                    logger.warning("In class %s.%s %s pattern '%s' "
                                   "did not match any existing logical property." % \
                                   (cls.__module__, cls.__name__, _dict_name, pat))
                    pass
                pass

            # now adds the exact matches (no wilcards) which override
            # the pattern-matches
            _resolved_dict.update((name, ai)
                                  for name, ai in _dict.iteritems()
                                  if name in log_props)

            # checks that all getter/setter have a corresponding logical property
            not_found = [name for name in _resolved_dict
                         if name not in log_props]

            if not_found:
                logger.warning("In class %s.%s logical %s were declared for"\
                                   "non-existant observables: %s" % \
                                   (cls.__module__, cls.__name__, _dict_name, str(not_found)))
                pass
            pass

        # creates the properties
        for name in log_props:
            # finds the getter
            ai_get = resolved_getdict.get(name, None)
            if ai_get:
                # decorator-based
                _getter = type(cls).get_getter(cls, name, ai_get.func,
                                               ai_get.has_args)
            else:
                # old style
                _getter = type(cls).get_getter(cls, name)
                if _getter is None:
                    raise RuntimeError("In class %s.%s logical observable '%s' "\
                                           "has no getter method" % \
                                           (cls.__module__, cls.__name__, name))
                pass

            # finds the setter
            ai_set = resolved_setdict.get(name, None)
            if ai_set:
                # decorator-based
                if ai_get:
                    _setter = type(cls).get_setter(cls, name,
                                                    ai_set.func, ai_set.has_args,
                                                    ai_get.func, ai_get.has_args)
                else:
                    # the getter is old style. _getter is already
                    # resolved wrt the name it may take, so
                    # getter_takes_name is False
                    _setter = type(cls).get_setter(cls, name,
                                                    ai_set.func, ai_set.has_args,
                                                    _getter, False)
                    pass
            else:
                # old style setter
                if ai_get:
                    _setter = type(cls).get_setter(cls, name,
                                                    None, None,
                                                    ai_get.func,
                                                    ai_get.has_args)
                else: _setter = type(cls).get_setter(cls, name)
                pass

            # here _setter can be None
            prop = property(_getter, _setter)
            setattr(cls, name, prop)
            real_log_props.add(name)
            pass

        # checks that all setters have a getter
        setters_no_getters = (set(resolved_setdict) - real_log_props) & log_props
        if setters_no_getters:
            logger.warning("In class %s.%s logical setters have no "
                           "getters: %s" % \
                               (cls.__module__, cls.__name__,
                                ", ".join(setters_no_getters)))
            pass

        return frozenset(real_log_props)



    def __create_conc_prop_accessors__(cls, prop_name, default_val):
        """Private method that creates getter and setter, and the
        corresponding property. This is used for concrete
        properties."""
        getter_name = "get_prop_%s" % prop_name
        setter_name = "set_prop_%s" % prop_name

        members_names = cls.__dict__.keys()

        # checks if accessors are already defined:
        if getter_name not in members_names:
            _getter = type(cls).get_getter(cls, prop_name)
            setattr(cls, getter_name, _getter)
        else:
            logger.debug("Custom member '%s' overloads generated getter of property '%s'" \
                             % (getter_name, prop_name))
            pass

        if setter_name not in members_names:
            _setter = type(cls).get_setter(cls, prop_name)
            setattr(cls, setter_name, _setter)
        else:
            logger.warning("Custom member '%s' overloads generated setter of property '%s'" \
                               % (setter_name, prop_name))
            pass

        # creates the property
        prop = property(getattr(cls, getter_name), getattr(cls, setter_name))
        setattr(cls, prop_name, prop)

        # creates the underlaying variable if needed
        varname = PROP_NAME % {'prop_name' : prop_name}
        if varname not in members_names:
            setattr(cls, varname, cls.create_value(varname, default_val))

        else: logger.warning("In class %s.%s automatic property builder found a "
                             "possible clashing with attribute '%s'" \
                                 % (cls.__module__, cls.__name__, varname))
        return

    def has_prop_attribute(cls, prop_name): # @NoSelf
        """This methods returns True if there exists a class attribute
        for the given property. The attribute is searched locally
        only"""
        props = getattr(cls, PROPS_MAP_NAME, {})

        return (cls.__dict__.has_key(prop_name) and
                type(cls.__dict__[prop_name]) != types.FunctionType)

    def check_value_change(cls, old, new): # @NoSelf
        """Checks whether the value of the property changed in type
        or if the instance has been changed to a different instance.
        If true, a call to model._reset_property_notification should
        be called in order to re-register the new property instance
        or type"""
        return  type(old) != type(new) or \
               isinstance(old, wrappers.ObsWrapperBase) and (old != new)

    def create_value(cls, prop_name, val, model=None): # @NoSelf
        """This is used to create a value to be assigned to a
        property. Depending on the type of the value, different values
        are created and returned. For example, for a list, a
        ListWrapper is created to wrap it, and returned for the
        assignment. model is different from None when the value is
        changed (a model exists). Otherwise, during property creation
        model is None"""

        if isinstance(val, tuple):
            # this might be a class instance to be wrapped
            # (thanks to Tobias Weber for
            # providing a bug fix to avoid TypeError (in 1.99.1)
            if len(val) == 3:
                try:
                    wrap_instance = isinstance(val[1], val[0]) and \
                        (isinstance(val[2], tuple) or
                         isinstance(val[2], list))
                except TypeError:
                    pass # not recognized, it must be another type of tuple
                else:
                    if wrap_instance:
                        res = wrappers.ObsUserClassWrapper(val[1], val[2])
                        if model: res.__add_model__(model, prop_name)
                        return res
                    pass
                pass
            pass

        elif isinstance(val, list):
            res = wrappers.ObsListWrapper(val)
            if model: res.__add_model__(model, prop_name)
            return res

        elif isinstance(val, dict):
            res = wrappers.ObsMapWrapper(val)
            if model: res.__add_model__(model, prop_name)
            return res

        return val


    # ------------------------------------------------------------
    #               Services
    # ------------------------------------------------------------

    # Override these:
    def get_getter(cls, prop_name, # @NoSelf
                   user_getter=None, getter_takes_name=False):
        """Returns a function wich is a getter for a property.
        prop_name is the name off the property.

        user_getter is an optional function doing the work. If
        specified, that function will be called instead of getting
        the attribute whose name is in 'prop_name'. 

        If user_getter is specified with a False value for
        getter_takes_name (default), than the method is used to get
        the value of the property. If True is specified for
        getter_takes_name, then the user_getter is called by
        passing the property name (i.e. it is considered a general
        method which receive the property name whose value has to
        be returned.)
        """
        if user_getter:
            if getter_takes_name: # wraps the property name
                def _getter(self): return user_getter(self, prop_name)
            else: _getter = user_getter
            return _getter

        def _getter(self): return getattr(self, # @DuplicatedSignature
                                          PROP_NAME % {'prop_name' : prop_name})
        return _getter


    def get_setter(cls, prop_name, # @NoSelf
                   user_setter=None, setter_takes_name=False,
                   user_getter=None, getter_takes_name=False):
        """Similar to get_getter, but for setting property
        values. If user_getter is specified, that it may be used to
        get the old value of the property before setting it (this
        is the case in some derived classes' implementation). if
        getter_takes_name is True and user_getter is not None, than
        the property name is passed to the given getter to retrieve
        the property value."""

        if user_setter:
            if setter_takes_name:
                # wraps the property name
                def _setter(self, val): return user_setter(self, prop_name, val)
            else: _setter = user_setter
            return _setter

        def _setter(self, val): setattr(self,
                                        PROP_NAME % {'prop_name' : prop_name},
                                        val)
        return _setter

    pass # end of class
# ----------------------------------------------------------------------



class ObservablePropertyMeta (PropertyMeta):
  """Classes instantiated by this meta-class must provide a method named
  notify_property_change(self, prop_name, old, new)"""
  def __init__(cls, name, bases, dict): # @NoSelf
    PropertyMeta.__init__(cls, name, bases, dict)
    return

  def get_getter(cls, prop_name, # @NoSelf
                 user_getter=None, getter_takes_name=False):
      """This implementation returns the PROP_NAME value if there
      exists such property. Otherwise there must exist a logical
      getter (user_getter) which the value is taken from.  If no
      getter is found, None is returned (i.e. the property cannot
      be created)"""

      has_prop_variable = cls.has_prop_attribute(prop_name)

      # WARNING! Deprecated
      has_specific_getter = hasattr(cls, GET_PROP_NAME % {'prop_name' : prop_name})
      has_general_getter = hasattr(cls, GET_GENERIC_NAME)

      if not (has_prop_variable or
              has_specific_getter or has_general_getter or user_getter):
          return None

      # when property variable is given, it overrides all the getters
      if has_prop_variable:
          if has_specific_getter or user_getter:
              logger.warning("In class %s.%s ignoring custom logical getter "
                             "for property '%s' as a corresponding "
                             "attribute exists" \
                                 % (cls.__module__, cls.__name__, prop_name))
              pass
          # user_getter is ignored here, so it has not to be passed up
          user_getter = None; getter_takes_name = False
      else:

          # uses logical getter. Sees if the getter needs to receive
          # the property name (i.e. if the getter is used for multiple
          # properties)
          if user_getter: pass
          else:
              if has_specific_getter:
                  # this is done to delay getter call, to have
                  # bound methods to allow overloading of getter in
                  # derived classes
                  def __getter(self):
                      _getter = getattr(self, GET_PROP_NAME % {'prop_name' : prop_name})
                      return _getter()
                  # previously it was simply:
                  # user_getter = getattr(cls, GET_PROP_NAME % {'prop_name' : prop_name})
                  user_getter = __getter
                  getter_takes_name = False
              else:
                  assert has_general_getter
                  def __getter(self, name):
                      _getter = getattr(self, GET_GENERIC_NAME)
                      return _getter(name)
                  # user_getter = getattr(cls, GET_GENERIC_NAME)
                  user_getter = __getter
                  getter_takes_name = True
                  pass
              pass
          pass

      return PropertyMeta.get_getter(cls, prop_name, user_getter, getter_takes_name)


  def get_setter(cls, prop_name, # @NoSelf
                 user_setter=None, setter_takes_name=False,
                 user_getter=None, getter_takes_name=False):
      """The setter follows the rules of the getter. First search
      for property variable, then logical custom setter. If no
      setter is found, None is returned (i.e. the property is
      read-only.)"""

      has_prop_variable = cls.has_prop_attribute(prop_name)

      # WARNING! These are deprecated
      has_specific_setter = hasattr(cls, SET_PROP_NAME % {'prop_name' : prop_name})
      has_general_setter = hasattr(cls, SET_GENERIC_NAME)

      if not (has_prop_variable or
              has_specific_setter or has_general_setter or user_setter):
          return None

      if has_prop_variable:
          if has_specific_setter or user_setter:
              logger.warning("In class %s.%s ignoring custom logical setter "
                             "for property '%s' as a corresponding "
                             "attribute exists" \
                                 % (cls.__module__, cls.__name__, prop_name))
              pass
          user_setter = user_getter = None
          setter_takes_name = getter_takes_name = False
      else:
          if user_setter: pass
          else:
              if has_specific_setter:
                  def __setter(self, val):
                      _setter = getattr(self, SET_PROP_NAME % {'prop_name' : prop_name})
                      _setter(val)
                      pass
                  user_setter = __setter
                  # user_setter = getattr(cls, SET_PROP_NAME % {'prop_name' : prop_name})
                  setter_takes_name = False
              else:
                  assert has_general_setter
                  def __setter(self, name, val):
                      _setter = getattr(self, SET_GENERIC_NAME)
                      _setter(name, val)
                      pass
                  user_setter = __setter
                  # user_setter = getattr(cls, SET_GENERIC_NAME)
                  setter_takes_name = True
                  pass
              pass
          pass

      # the final setter is a combination of a basic setter, and
      # the getter (see how inner_{getter,setter} are used in
      # _setter below)
      _inner_setter = PropertyMeta.get_setter(cls, prop_name,
                                              user_setter, setter_takes_name,
                                              user_getter, getter_takes_name)


      _inner_getter = type(cls).get_getter(cls, prop_name, user_getter, getter_takes_name)

      def _setter(self, val):
          old = _inner_getter(self)
          new = type(self).create_value(prop_name, val, self)
          _inner_setter(self, new)
          if type(self).check_value_change(old, new):
              self._reset_property_notification(prop_name, old)
              pass
          self.notify_property_value_change(prop_name, old, val)
          return
      return _setter

  pass # end of class
# ----------------------------------------------------------------------


try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading # @UnusedImport

class ObservablePropertyMetaMT (ObservablePropertyMeta):
    """This class provides multi-threading support for accessing
    properties, through a locking mechanism. It is assumed a lock is
    owned by the class that uses it. A Lock object called _prop_lock
    is assumed to be a member of the using class. see for example class
    ModelMT"""
    def __init__(cls, name, bases, dict): # @NoSelf @ReservedAssignment
        ObservablePropertyMeta.__init__(cls, name, bases, dict)
        return

    def get_setter(cls, prop_name, # @NoSelf
                   user_setter=None, setter_takes_name=False,
                   user_getter=None, getter_takes_name=False):
        """The setter follows the rules of the getter. First search
        for property variable, then logical custom getter/seter pair
        methods"""

        _inner_setter = ObservablePropertyMeta.get_setter(cls, prop_name,
                                                          user_setter, setter_takes_name,
                                                          user_getter, getter_takes_name)
        def _setter(self, val):
            if hasattr(self, '_prop_lock'):
                with self._prop_lock:
                    return _inner_setter(self, val)
            else:
                return _inner_setter(self, val)
        return _setter

    pass # end of class


try:
    from sqlobject import Col # @UnresolvedImport
    from sqlobject.inheritance import InheritableSQLObject  # @UnresolvedImport
    from sqlobject.events import listen, RowUpdateSignal  # @UnresolvedImport

    class ObservablePropertyMetaSQL (InheritableSQLObject.__metaclass__,
                                   ObservablePropertyMeta):
        """Classes instantiated by this meta-class must provide a method
        named notify_property_change(self, prop_name, old, new)"""

        def __init__(cls, name, bases, dict): # @NoSelf @ReservedAssignment
            InheritableSQLObject.__metaclass__.__init__(cls, name, bases, dict)
            ObservablePropertyMeta.__init__(cls, name, bases, dict)

            listen(cls.update_listener, cls, RowUpdateSignal)
            return

        def __create_conc_prop_accessors__(cls, prop_name, default_val): # @NoSelf
            if not isinstance(default_val, Col):
                # this is not a SQLObject column (likely a normal concrete
                # observable property)
                ObservablePropertyMeta.__create_conc_prop_accessors__(
                    cls,
                    prop_name,
                    default_val
                )
            return

        def update_listener(cls, instance, kwargs): # @NoSelf
            conc_pnames, _ = type(cls).__get_observables_sets__(cls)
            for k in kwargs:
                if k in conc_pnames:
                    _old = getattr(instance, k)
                    _new = kwargs[k]
                    instance.notify_property_value_change(k, _old, _new)
                    pass
                pass
            return

        pass # end of class
except:
    pass
try:
    from gobject import GObjectMeta
    class ObservablePropertyGObjectMeta (ObservablePropertyMeta, GObjectMeta):
        pass
    class ObservablePropertyGObjectMetaMT (ObservablePropertyMetaMT, GObjectMeta):
        pass
except:
    class ObservablePropertyGObjectMeta (ObservablePropertyMeta):
        pass
    class ObservablePropertyGObjectMetaMT (ObservablePropertyMetaMT):
        pass
    pass

