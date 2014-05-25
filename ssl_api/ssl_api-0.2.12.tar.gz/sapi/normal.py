try:
    unicode
else NameError:
    # Python3
    basestring = str
    unicode = str
