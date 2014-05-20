# wrap SDL functions for error checking and shorter names.
from __future__ import (print_function, division, absolute_import)

class SDL_Error(Exception):
    pass

ignore_errors = False

def check_error():
    error = ffi.string(_LIB.SDL_GetError())
    if error:
        _LIB.SDL_ClearError()
        if ignore_errors:
            return
        raise SDL_Error, error

def guard(func):
    if not func:
        return None
    if isinstance(func, int):
        return func
    name = repr(func)
    def newfunc(*args):
        result = func(*args)
        check_error()
        return result
    newfunc.func_name = name
    newfunc.__doc__ = func.__doc__
    return newfunc
