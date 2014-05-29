# -*- mode:python; coding:utf-8; tab-width:4 -*-

##-- WARNING: be ware no including here nothing about encoding: JSON, BSON, etc.


def any_to_marshable(value):
    if isinstance(value, str):
        return unicode(value)

    if isinstance(value, (unicode, int, bool, float, long)):
        return value

    if value is None:
        return value

    if hasattr(value, 'to_marshable'):
        return value.to_marshable()

    if isinstance(value, (list, tuple)):
        return [any_to_marshable(x) for x in value]

    if isinstance(value, dict):
        return dict_to_marshable(value)

    # last resort
    return class_to_marshable(value)


def dict_to_marshable(value):
    assert isinstance(value, dict)

    retval = {}
    for k, v in value.items():
        retval[k] = any_to_marshable(v)

    return retval


def class_to_marshable(value):
    retval = {}
    for name in dir(value):
        if name.startswith("_"):
            continue

        attr = getattr(value, name)
        if callable(attr):
            continue

        retval[name] = any_to_marshable(attr)

    return retval


def exception_to_marshable(exc):
    assert isinstance(exc, Exception)
    return [exc.__class__.__name__, str(exc)]


def get_typecode(value):
    if isinstance(value, dict):
        return value.get("wise_typecode")

    return None
