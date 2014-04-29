'''
Created on 21/May/2012

@author: William Schoenell
@note: Based Andre's starlighttable.py

'''

import os
import gzip
import bz2

import asciitable
import atpy
from atpy.asciitables import read_ascii

def _getSDSSInputFileVersion():
    return '7xt'


def read_set(self, filename):
    '''
    Read STARLIGHT 4 column file.

    William@IAA - 02July2012

    @param filename: STARLIGHT input filename
    '''
    
    self.reset()
    ascii = True

    if not os.path.exists(filename):
        raise Exception('File not found: %s' % filename)

    if filename.endswith('.gz'):
        f = gzip.GzipFile(filename)
    elif filename.endswith('.bz2'):
        f = bz2.BZ2File(filename)
    else:
        f = open(filename)

    if ascii:
        read_ascii(self, f, guess=False, names=['lambda', 'flux', 'error', 'flag'])
    
    f.close()
    
    self.keywords['filename'] = os.path.basename(filename)
    self.table_name = 'starlight_input'

####################################################################################################
