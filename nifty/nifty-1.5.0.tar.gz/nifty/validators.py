# -*- coding: utf-8 -*-
"""Objects responsible for performing validations."""
import os


class Validator(object):
  """Generic validator, base class for specific validator objects."""

  def validate(self, val):
    """Method for validating an object. Subclasses
    should override this method.
    """
    raise NotImplementedError()

  def parse_and_validate(self, val):
    """Method for parsing an input and then perform validation.
    Subclassses can override this method if needed.
    """
    return self.validate(val)


class IntegerValidator(object):
  """Validator for validating integers."""

  def validate(self, val):
    if not isinstance(val, int):
      raise ValueError()
    return val

  def parse_and_validate(self, val):
    try:
      val = int(val)
    except:
      raise ValueError()

    return self.validate(val)


class PositiveIntegerValidator(IntegerValidator):
  """Validator for validating positive integers."""

  def validate(self, val):
    val = super(PositiveIntegerValidator, self).validate(val)
    if val < 0:
      raise ValueError('Integer must be greater than or equal to zero')
    return val


class NiftyCmdlineOptionsValidator(Validator):
  """Validator for validating nifty command line options and arguments."""

  def validate(self, value):
    options, args = value

    if not args:
      raise ValueError('No config file specified')

    config_path = args[0]

    if not os.path.exists(config_path):
      raise ValueError('Invalid config file specified')

    if not options.list and not options.command:
      raise ValueError('No command specified')

    return value


class NiftyHandlerInputValidator(Validator):
  """Validator for validating user inputs of a `NiftyHandler` object."""

  def __init__(self):
    self.positive_integer_validator = PositiveIntegerValidator()

  def parse_and_validate(self, val):
    paths = [path.strip() for path in val.split(',')]

    valid_paths = []

    for path in paths:
      self.validate_path(path)
      valid_paths.append(path)

    return valid_paths

  def validate_path(self, path):
    indices = path.split('.')
    for index in indices:
      self.positive_integer_validator.parse_and_validate(index)