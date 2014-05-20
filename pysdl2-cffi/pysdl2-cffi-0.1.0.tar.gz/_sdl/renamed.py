# "pretty" names without the NAMESPACE_ prefixes...
from __future__ import absolute_import

from . import lib

def _init(prefix="SDL_"):
    # allowed even though they don't start with prefix:
    whitelist = ['ALL_PIXELFORMATS',
                 'SDLError',
                 'Struct',
                 'ffi']
    here = globals()
    import re
    constant = re.compile(prefix + "[A-Z][A-Z]+")
    for name in dir(lib):
        value = getattr(lib, name)
        pretty_name = name
        if not name.startswith(prefix):
            if not name in whitelist:
                continue
        elif constant.match(name) or isinstance(value, type):
            pretty_name = name[4:]
        else:
            pretty_name = name[4].lower() + name[5:]
        here[pretty_name] = value

_init()