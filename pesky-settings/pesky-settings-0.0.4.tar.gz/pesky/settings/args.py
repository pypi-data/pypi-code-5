# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

from pesky.settings.errors import ConfigureError

def parse_args(args, *spec, **kwargs):
    """
    Returns a tuple containing arguments conforming to *spec.  if the number of
    command arguments is less than minimum or greater than maximum, or if any
    argument cannot be validated, ConfigureError is raised.  Any optional arguments
    which are not specified are passed through unmodified.

    :param spec: a list of validator functions
    :type spec: [callable]
    :param minimum: The number of required arguments
    :type: int
    :param maximum: The numer of required + optional arguments
    :type maxmimum: int
    :param names: a list of argument names corresponding to each validator
    :type names: [str]
    :returns: a tuple containing arguments conforming to spec
    :rtype: (object)
    """
    try:
        minimum = kwargs['minimum']
    except:
        minimum = None
    try:
        maximum = kwargs['maximum']
    except:
        maximum = None
    try:
        names = kwargs['names']
    except:
        names = None
    if maximum != None and len(args) > maximum:
        raise ConfigureError("extra trailing arguments")
    parsed = args[:]
    for i in range(len(spec)):
        try:
            validator = spec[i]
            parsed[i] = validator(parsed[i])
        except IndexError:
            if minimum == None or i < minimum:
                if names != None and i < len(names):
                    raise ConfigureError("missing argument " + names[i])
                raise ConfigureError("missing argument")
        except Exception, e:
            if names != None and i < len(names):
                raise ConfigureError("failed to parse argument %s: %s" % (names[i], str(e)))
            raise ConfigureError("failed to parse argument: %s" % str(e))
    return tuple(parsed)
