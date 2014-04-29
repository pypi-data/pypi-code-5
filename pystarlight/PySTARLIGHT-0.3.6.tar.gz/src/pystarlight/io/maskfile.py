'''
Created on 04/04/2013

@author: lacerda
'''

import numpy as np
import os

def read(self, maskfile):
    '''
        Reads StarlightChains_v04.for maskfile
        @param maskfile: Starlight input maskfile.
    '''
    self.reset()
    self.keywords['arq_mask'] = os.path.basename(maskfile)

    dt = np.dtype([ ('l_low', '>f8'), ('l_up', '>f8'), ('weight', '>f8'), ('name', 'S60') ])
    mdata = np.loadtxt(maskfile, dtype = dt, skiprows = 1, usecols = (0, 1, 2, 3))

    self.table_name = 'maskfile'
    self.add_column('l_low', mdata['l_low'])
    self.add_column('l_up', mdata['l_up'])
    self.add_column('weight', mdata['weight'])
    self.add_column('name', mdata['name'])
