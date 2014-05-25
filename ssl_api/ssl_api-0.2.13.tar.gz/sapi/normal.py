try:
    unicode
except NameError:
    # Python3
    basestring = str
    unicode = str
