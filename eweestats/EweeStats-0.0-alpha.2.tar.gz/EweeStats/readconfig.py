# -*- coding: utf-8 -*-
#
#  readconfig.py
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
import re
import shlex

def read_config():
    """
    Reads configuration file to set up sensors
    """
    conf_file = os.path.join(
        '/etc/eweestats', 'eweestats.conf')
    
    if not os.path.isfile(conf_file):
        raise NameError('no configuration file')
        sys.exit()
    
    sensor_dict = {}
    
    with open(conf_file, 'r') as c:
        for line in c:
            part = shlex.split(line, True)
            if part == []:
                continue
            print(part)
            if re.search(r'sensors', part[0]) is not None:
                analogSensors = int(part[2])
            elif re.match(r'^A[0-9]{1,2}$', part[0]) is not None:
                pin_number = part[0].replace('A', '')
                sensor_dict[pin_number] = part[2]
            elif re.match(r'^savedir', part[0]) is not None:
                save_dir = part[2]
            elif re.match(r'^graphname', part[0]) is not None:
                graph_name = part[2]
    
    graph_name = os.path.join(save_dir, graph_name)
    print(analogSensors)
    print(sensor_dict)
    print(save_dir)
    print(graph_name)
    
    return analogSensors, sensor_dict, save_dir, graph_name

    
if __name__ == '__main__':
    read_config()

    
