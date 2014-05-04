#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  convert_data.py
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

def convert(value_list):
    """
    :param value_list: liste des valeurs relevées
    :type value_list: list

    :returns: converted datas
    :rtype: list
    """

    # Config : links each pin to a sensor type
    sensor_list = ['pot', 'pot']
    value_real = []
    for i in value_list:
        value_real.append(0.0)

    for i, elt in enumerate(sensor_list):
        if elt == 'pot':
            convert_pot(i, value_list, value_real)

    return value_real

def convert_pot(pinToPot, value_list, value_real):
    """
    :param pinToPot: numéro du pin relié au potentiomètre
    :type pinToPot: integer

    :param valueList: valeurs non transformées
    :type valueList: list

    :param valueReal: liste devant acceuillir les valeurs transformées
    :type valueReal: list

    :returns: nombre converti à la case du numéro du pin
    :rtype: integer
    """
    value_real[pinToPot] = value_list[pinToPot] * 5

    return value_real

