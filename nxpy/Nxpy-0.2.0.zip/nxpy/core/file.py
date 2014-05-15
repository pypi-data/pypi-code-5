# nxpy.core package ----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
File related utilities.

"""

# Python 2.5 compatibility
from __future__ import with_statement    

import itertools
import os


def compare(file1, file2, ignore_eof=True):
    r"""
    Compare two text files for equality.
    If *ignore_eof* is *True*, end of line characters are not considered.
    
    """
    if isinstance(file1, basestring):
        f1 = open(file1, "r")
    else:
        f1 = file1
        f1.seek(0, os.SEEK_SET)
    if isinstance(file2, basestring):
        f2 = open(file2, "r")
    else:
        f2 = file2
        f2.seek(0, os.SEEK_SET)
    with f1:
        with f2:
            for l1, l2 in itertools.imap(None, f1, f2):
                if ( ( not ignore_eof and l1 != l2 ) or 
                     ( ignore_eof and l1.rstrip("\r\n") != l2.rstrip("\r\n") ) ):
                    return False
            return True
