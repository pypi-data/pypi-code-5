# Base class for struct helpers.

from .dso import ffi

class Struct(object):
    """
    Wrap a cffi structure in a Python class, hiding allocation and
    dereferencing.
    """
    def __init__(self, cdata=ffi.NULL):
        if cdata == ffi.NULL:
            cdata = ffi.new("%s *" % (self.__class__.__name__))
        self.cdata = cdata

    def __getattr__(self, attr):
        # XXX and if the attribute's value is another struct, return its wrapper
        return getattr(self.cdata[0], attr)

    def __setattr__(self, attr, value):
        if attr == 'cdata':
            super(Struct, self).__setattr__(attr, value)
        else:
            setattr(self.cdata[0], attr, value)

def unbox(struct_or_cdata):
    """Return a Struct's underlying storage to pass to low-level ffi calls."""
    if isinstance(struct_or_cdata, Struct):
        return struct_or_cdata.cdata
    return struct_or_cdata

def box(struct_or_cdata):
    if isinstance(struct_or_cdata): pass

    return struct_or_cdata