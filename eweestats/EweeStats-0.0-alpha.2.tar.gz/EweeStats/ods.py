# -*- encoding: utf-8 -*-
#
#  ods.py
#  
#  Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


import ezodf2
import os
import sys
import string

def write_ods(dataDir, analogSensors, listValueLists, timelist):
    

    filename = os.path.join(dataDir, 'ewee_data.ods')
    ods = ezodf2.newdoc(doctype = 'ods', filename = '{f}'.format(f = filename))

    sheet = ezodf2.Sheet('SHEET', size = (len(timelist), analogSensors + 1))
    ods.sheets += sheet
    
    # timestamp writing
    for i, elt in enumerate(timelist):
        sheet['A{line}'.format(line = i + 1)].set_value(float(elt))
    
    # Data writing
    for i in range(analogSensors):
        for j, elt in enumerate(listValueLists[i]):
            sheet['{letter}{line}'.format(
                letter = string.uppercase[i + 1],
                line = j + 1
                )].set_value(elt)
            
    ods.save()
    
