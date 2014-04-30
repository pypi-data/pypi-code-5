from __future__ import absolute_import

import copy


class CaseClass(object):
  """
  A data-only class. Provides object equality, iteration, constructor, and
  (shallow) copy logic via definition of `__slots__`.

  Parameters
  ----------
  args, kwargs : anything
      attributes to set, as defined in slots
  """

  # fill this in to construct a case class
  # __slots__ = ["x", "y"]

  def __init__(self, *args, **kwargs):
    if len(args) > len(self.__slots__):
      raise KeyError(
        "Too many arguments. {} only accepts {} parameters"
        .format(self.__class__.__name__, len(self.__slots__))
      )

    kwargs.update({k:v for k, v in zip(self.__slots__, args)})

    for k, v in kwargs.items():
      if k not in self.__slots__:
        raise KeyError(
          "'{}' is not a valid attribute for {}"
          .format(k, self.__class__.__name__)
        )
      else:
        setattr(self, k, v)

  def __unicode__(self):
    name   = self.__class__.__name__
    values = [getattr(self, k, '<undefined>') for k in self.__slots__]
    return u"{}({})".format(name, ", ".join(map(unicode, values)))

  def __str__(self):
    return str(self.__unicode__)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    o = object()

    # type checks
    if not isinstance(other, self.__class__): return False
    if not isinstance(self, other.__class__): return False

    # field checks
    for k in self.__slots__:
      if getattr(self, k, o) != getattr(other, k, o):
        return False
    return True

  def __ne__(self, other):
    return not self.__eq__(other)

  def __iter__(self, other):
    for k in self.__slots__:
      return getattr(self, k)

  def copy(self, **kwargs):
    """
    Copy a CaseClass-derived object. WARNING! This circumvents calling
    __init__, so if you have any logic in there beyond setting the variables in
    __slots__, it will not be executed!
    """
    attrs = {k:getattr(self, k) for k in self.__slots__}
    attrs.update(kwargs)
    result = copy.copy(self)
    for k, v in attrs.items():
      setattr(result, k, v)
    return result

  @classmethod
  def build(cls, config):
    relevant = {k:v for k,v in config.items() if k in cls.__slots__}
    return cls(**relevant)
