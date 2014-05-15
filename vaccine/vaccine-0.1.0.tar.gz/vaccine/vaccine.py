"""
A simple dependency injection service.
"""
import inspect
import types

from .exceptions import VaccineException


class Vaccine(object):
  """
  Create a new dependency injection environment.
  """

  def __init__(self):
    self.registry = {}

  def get(self, key):
    """Retrieve value for a key"""
    if key not in self.registry:
      raise VaccineException(
        ("The key '{}' was not registered to a value or a"
         " class").format(key)
      )
    v, evaluated = self.registry[key]
    if not evaluated:
      self.registry[key] = v(), True
    return self.registry[key][0]

  def requires(self, **bindings):
    """Bind function/class constructor arguments to keys this Vaccine will
    provide values for"""
    def decorator(func):

      # get argument names
      if isinstance(func, types.FunctionType):
        argnames = inspect.getargspec(func).args
        defaults = inspect.getargspec(func).defaults or []
      else:
        argnames = inspect.getargspec(func.__init__).args[1:]
        defaults = inspect.getargspec(func.__init__).defaults or []

      def decorated(*args, **kwargs):
        a = {}

        # merge all arguments into a dict
        a = dict(zip(argnames, args))
        a.update(kwargs)

        # fill in whatever's missing with registry values
        for argname, key in bindings.items():
          if argname not in a:
            a[argname] = self.get(key)


        remaining = [
          argname for argname in argnames[0:len(argnames)-len(defaults)]
          if argname not in a
        ]
        if len(remaining) > 0:
          raise VaccineException(
            ("The following arguments were not registered for '{}': {}")
            .format(func.__name__, ", ".join(map(unicode, remaining)))
          )
        else:
          return func(**a)
      return decorated
    return decorator

  def provides(self, key):
    """Register this function as providing for `key`"""
    if key in self.registry:
      raise VaccineException(
        "'{}' is already registered to '{}'".format(key,
        self.registry[key][0])
      )

    def decorator(func):
      self.registry[key] = (func, False)
      return func
    return decorator

  def register(self, key, value):
    """Registry an already-resolved value"""
    if key in self.registry:
      raise VaccineException(
        "'{}' is already registered to '{}'".format(key,
        self.registry[key][0])
      )
    self.registry[key] = (value, True)

  def unregister(self, key):
    """
    Unregister a dependency. If no dependency is registered under the given
    key, does nothing.
    """
    if key in self.registry:
      del self.registry[key]
