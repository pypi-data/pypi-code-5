'''collection of routines to support python 2&3 code in this package'''

import sys


def iteritems(dct):
    '''return the appropriate method'''
    if sys.version_info < (3, ):
        return dct.iteritems()
    else:
        return dct.items()
