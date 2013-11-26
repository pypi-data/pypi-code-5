#!/usr/bin/env python

# $Id$
"""
A module for reading and writing FITS files and manipulating their
contents.

A module for reading and writing Flexible Image Transport System
(FITS) files.  This file format was endorsed by the International
Astronomical Union in 1999 and mandated by NASA as the standard format
for storing high energy astrophysics data.  For details of the FITS
standard, see the NASA/Science Office of Standards and Technology
publication, NOST 100-2.0.

For detailed examples of usage, see the `PyFITS User's Manual
<http://stsdas.stsci.edu/download/wikidocs/The_PyFITS_Handbook.pdf>`_.

"""


# The existing unit tests, anyways, only require this in pyfits.hdu.table,
# but we should still leave new division here too in order to avoid any nasty
# surprises
from __future__ import division  # confidence high


"""
        Do you mean: "Profits"?

                - Google Search, when asked for "PyFITS"
"""

import os
import sys
import urllib
import warnings

import pyfits.py3compat

# Public API compatibility imports
import pyfits.card
import pyfits.column
import pyfits.convenience
import pyfits.diff
import pyfits.hdu

from pyfits.card import *
from pyfits.column import *
from pyfits.convenience import *
from pyfits.diff import *
from pyfits.fitsrec import FITS_record, FITS_rec
from pyfits.hdu import *

from pyfits.hdu.hdulist import fitsopen as open
from pyfits.hdu.image import Section
from pyfits.hdu.table import new_table
from pyfits.header import Header


# Additional imports used by the documentation (some of which should be
# restructured at some point)
from pyfits.verify import VerifyError


# Set module-global boolean variables--these variables can also get their
# values from environment variables
GLOBALS = [
    # Variable name                       # Default
    ('ENABLE_RECORD_VALUED_KEYWORD_CARDS', True),
    ('EXTENSION_NAME_CASE_SENSITIVE',      False),
    ('STRIP_HEADER_WHITESPACE',            True),
    ('USE_MEMMAP',                         True)
]

for varname, default in GLOBALS:
    try:
        locals()[varname] = bool(int(os.environ.get('PYFITS_' + varname,
                                                    default)))
    except ValueError:
        locals()[varname] = default


__all__ = (pyfits.card.__all__ + pyfits.column.__all__ +
           pyfits.convenience.__all__ + pyfits.diff.__all__ +
           pyfits.hdu.__all__ +
           ['FITS_record', 'FITS_rec', 'open', 'Section', 'new_table',
            'Header', 'VerifyError', 'TRUE', 'FALSE'] +
           [g[0] for g in GLOBALS])


# These are of course deprecated, but a handful of external code still uses
# them
TRUE = True
FALSE = False


# Warnings routines
_formatwarning = warnings.formatwarning


def formatwarning(message, category, filename, lineno, line=None):
    if issubclass(category, UserWarning):
        return unicode(message) + '\n'
    else:
        if sys.version_info[:2] < (2, 6):
            # Python versions prior to 2.6 don't support the line argument
            return _formatwarning(message, category, filename, lineno)
        else:
            return _formatwarning(message, category, filename, lineno, line)

warnings.formatwarning = formatwarning
warnings.filterwarnings('always', category=UserWarning, append=True)


class ErrorURLopener(urllib.FancyURLopener):
    """A class to use with `urlretrieve` to allow `IOError` exceptions to be
    raised when a file specified by a URL cannot be accessed.

    """

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        raise IOError((errcode, errmsg, url))

urllib._urlopener = ErrorURLopener()  # Assign the locally subclassed opener
                                     # class to the urllibrary
urllib._urlopener.tempcache = {}  # Initialize tempcache with an empty
                                 # dictionary to enable file cacheing


__credits__ = """

Copyright (C) 2004 Association of Universities for Research in Astronomy (AURA)

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above
       copyright notice, this list of conditions and the following
       disclaimer in the documentation and/or other materials provided
       with the distribution.

    3. The name of AURA and its representatives may not be used to
       endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY AURA ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL AURA BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""
