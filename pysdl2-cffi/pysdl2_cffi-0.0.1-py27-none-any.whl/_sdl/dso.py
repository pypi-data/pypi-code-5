# dlopen the SDL library.

import sys

from .cdefs import ffi

if sys.platform == 'darwin':
    _LIB = ffi.dlopen('/Library/Frameworks/SDL2.framework/SDL2')
else:
    _LIB = ffi.dlopen("libSDL2.so")
