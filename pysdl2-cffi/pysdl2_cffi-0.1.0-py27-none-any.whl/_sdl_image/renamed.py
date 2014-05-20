# "pretty" names without the NAMESPACE_ prefixes...
from __future__ import absolute_import

from . import image

def _init():
    here = globals()
    import re
    constant = re.compile("IMG_[A-Z][A-Z]+")
    for name in dir(image):
        if not name.startswith("IMG_"):
            pass
        elif constant.match(name):
            pretty_name = name[4:]
        else:
            pretty_name = name[4].lower() + name[5:]
        here[pretty_name] = getattr(image, name)

_init()