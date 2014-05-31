# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import os, datetime, shlex, re

from pesky.settings.args import parse_args
from pesky.settings.errors import ConfigureError

class Section(object):
    """
    A group of configuration values which share a common purpose.

    :param name: The name of the section.
    :type name: str
    :param options: The parent :class:`Settings` instance.
    :type options: :class:`ConfigParser.RawConfigParser`
    :param cwd: the current working directory
    :type cwd: str
    """

    def __init__(self, name, options, cwd):
        self.name = name
        self._options = options
        self._cwd = cwd

    def get_str(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a str.  If there is no configuration value in the section
        called `name`, then return the value specified by `default`.  Note that
        `default` is returned unmodified (i.e. not coerced into a string).
        This makes it easy to detect if a configuration value is not present
        by setting `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The string value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        s = self._options.get(self.name, name)
        if s == None:
            return default
        return s.strip()

    def get_int(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a int.  If there is no configuration value in the section
        called `name`, then return the value specified by `default`.  Note that
        `default` is returned unmodified (i.e. not coerced into an int).
        This makes it easy to detect if a configuration value is not present
        by setting `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The int value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        if self._options.get(self.name, name) == None:
            return default
        return self._options.getint(self.name, name)

    def get_bool(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a bool.  If there is no configuration value in the section
        called `name`, then return the value specified by `default`.  Note that
        `default` is returned unmodified (i.e. not coerced into a bool).
        This makes it easy to detect if a configuration value is not present
        by setting `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The bool value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        if self._options.get(self.name, name) == None:
            return default
        return self._options.getboolean(self.name, name)

    def get_float(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a float.  If there is no configuration value in the section
        called `name`, then return the value specified by `default`.  Note that
        `default` is returned unmodified (i.e. not coerced into a float).
        This makes it easy to detect if a configuration value is not present
        by setting `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The float value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        if self._options.get(self.name, name) == None:
            return default
        return self._options.getfloat(self.name, name)

    def get_path(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a str and normalized as a filesystem absolute path.  If
        there is no configuration value in the section called `name`, then
        return the value specified by `default`.  Note that `default` is
        returned unmodified (i.e. not coerced into a string).  This makes it
        easy to detect if a configuration value is not present by setting
        `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The string value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        path = self._options.get(self.name, name)
        if path == None:
            return default
        return os.path.normpath(os.path.join(self._cwd, path))

    def get_list(self, name, default=None, coerce=str):
        """
        Returns the configuration value associated with the specified `name`,
        coerced into a list of values with the specified `type`.  If
        there is no configuration value in the section called `name`, then
        return the value specified by `default`.  Note that `default` is
        returned unmodified (i.e. not coerced into a list).  This makes it
        easy to detect if a configuration value is not present by setting
        `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :param coerce: The coercion function to apply to each value
        :type name: callable
        :returns: a list of coerced values, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        l = self._options.get(self.name, name)
        if l == None:
            return default
        try:
            return map(coerce, shlex.split(l))
        except Exception, e:
            raise ConfigureError("failed to parse configuration item [%s]=>%s: %s" % (
                self.name, name, e))

    def get_args(self, name, *spec, **kwargs):
        """
        """
        default = None
        if 'default' in kwargs:
            default = kwargs['default']
            del kwargs['default']
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        args = shlex.split(self._options.get(self.name, name))
        return parse_args(args, *spec, **kwargs)

    def get_timedelta(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a timedelta.  If there is no configuration value in the
        section called `name`, then return the value specified by `default`.
        Note that `default` is returned unmodified (i.e. not coerced into a
        timedelta).  This makes it easy to detect if a configuration value
        is not present by setting `default` to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The timedelta value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        string = self._options.get(self.name, name)
        if string == None:
            return default
        string = string.strip()
        tokens = [t for t in string.split(' ') if t != '']
        try:
            if len(tokens) < 2:
                raise Exception("invalid timedelta " + string)
            value = int(tokens[0])
            units = tokens[1].lower()
            if units in ('micro', 'micros', 'microsecond', 'microseconds'):
                return datetime.timedelta(microseconds=value)
            if units in ('milli', 'millis', 'millisecond', 'milliseconds'):
                return datetime.timedelta(milliseconds=value)
            if units in ('second', 'seconds'):
                return datetime.timedelta(seconds=value)
            if units in ('minute', 'minutes'):
                return datetime.timedelta(minutes=value)
            if units in ('hour', 'hours'):
                return datetime.timedelta(hours=value)
            if units in ('day', 'days'):
                return datetime.timedelta(days=value)
            if units in ('week', 'weeks'):
                return datetime.timedelta(weeks=value)
        except Exception, e:
            raise ConfigureError("failed to parse configuration item [%s]=>%s: %s" % (
                self.name, name, str(e)))

    def get_size(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a long representing size in bytes.  If there is no
        configuration value in the section called `name`, then return the
        value specified by `default`.  Note that `default` is returned
        unmodified (i.e. not coerced into a long).  This makes it easy to
        detect if a configuration value is not present by setting `default`
        to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The long value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        string = self._options.get(self.name, name)
        if string == None:
            return default
        string = string.strip()
        tokens = [t for t in string.split(' ') if t != '']
        try:
            if len(tokens) < 2:
                raise Exception("invalid size " + string)
            value = long(tokens[0])
            units = tokens[1].lower()
            if units in ('kb', 'kilo', 'kilobyte', 'kilobytes'):
                return value * 1024
            if units in ('mb', 'mega', 'megabyte', 'megabytes'):
                return value * 1024 * 1024
            if units in ('gb', 'giga', 'gigabyte', 'gigabytes'):
                return value * 1024 * 1024 * 1024
            if units in ('tb', 'tera', 'terabyte', 'terabytes'):
                return value * 1024 * 1024 * 1024 * 1024
            if units in ('pb', 'peta', 'petabyte', 'petabytes'):
                return value * 1024 * 1024 * 1024 * 1024 * 1024
        except Exception, e:
            raise ConfigureError("failed to parse configuration item [%s]=>%s: %s" % (
                self.name, name, str(e)))

    def get_percent(self, name, default=None):
        """
        Returns the configuration value associated with the specified name,
        coerced into a float representing a percentage.  If there is no
        configuration value in the section called `name`, then return the
        value specified by `default`.  Note that `default` is returned
        unmodified (i.e. not coerced into a float).  This makes it easy to
        detect if a configuration value is not present by setting `default`
        to None.

        :param name: The configuration setting name.
        :type name: str
        :param default: The value to return if a value is not found.
        :returns: The float value, or the default value.
        """
        if self.name == None or not self._options.has_option(self.name, name):
            return default
        string = self._options.get(self.name, name)
        if string == None:
            return default
        string = string.strip()
        try:
            m = re.match(r'(0\.\d+|[1-9]\d*\.\d+|\d+)\s*%', string)
            if m is None:
                raise Exception("invalid percentage " + string)
            return float(m.group(1)) / 100.0
        except Exception, e:
            raise ConfigureError("failed to parse configuration item [%s]=>%s: %s" % (
                self.name, name, str(e)))

    def set(self, name, value):
        """
        Modify the configuration setting.  value must be a string.
        """
        if not isinstance(value, str):
            raise ConfigureError("failed to modify configuration item [%s]=>%s: value is not a string" % (
            self.name, name))
        self._options.set(self.name, name, value)

    def remove(self, name):
        """
        Remove the configuration setting.  Internally this sets the configuration
        value to None.
        """
        self._options.set(self.name, name, None)
