#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  create_files.py
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

import os
import sys

def create_files(datapath, graph_name):
    """
    :returns: graphname
    :rtype: string
    """
    
    # Create directory to save datas
    if not os.path.isdir(datapath):
        os.makedirs(datapath)
    
    # Create graph symlink
    web_root = '/var/www'
    if os.path.isfile(os.path.join(web_root, graph_name)):
                os.remove(os.path.join(web_root, graph_name))
    os.symlink(os.path.join(datapath, graph_name),
               os.path.join(web_root, graph_name))

def open_files(analogSensors, datapath):
    """
    :param analogSensors: number of sensors wired
    :type analogSensors: integer
    
    :param datapath: directory in which we save datas
    :type datapath: string
    
    :returns: list of opened files
    :rtype: list
    """
    
    file_list = []
    for i in range(analogSensors):
        filename = "data_{i}".format(i = str(i))
        filepath = os.path.join(datapath, filename)
        data_file = open(filepath, 'w+')
        file_list.append(data_file)

    filepath = os.path.join(datapath, 'timestamp')
    time_file = open(filepath, 'w+')
    print(file_list)
    
    return file_list, time_file


