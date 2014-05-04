# -*- coding: utf-8 -*-
#
#  graph.py
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


import pygal
import os
import sys

def create_graph(
    analogSensors, listValueLists, timelist, dataDir, graphName):
    """
    Création du graphique à l'aide de pygal
    
    :param analogSensors: nombre de capteurs
    :type analogSensors: integer
    
    :param listValueLists: liste de listes des valeurs
    :type listValueLists: list of lists
    
    :param timelist: horodatage
    :type timelist: list of strings
    
    :param dataDir: dossier contenant les fichiers
    :type dataDir: string

    :param graphName: nom du fichier de graph
    :type graphName: string

    :returns: 0
    """

    # Graph file name
    graphTempName = graphName.replace('.svg', '.svg.tmp')

    linechart                   = pygal.Line()
    linechart.x_label_rotation  = 20
    linechart.show_dots         = False
    linechart.human_readable    = True
    linechart.title             = 'Tension en fonction du temps'
    linechart.x_title           = 'Temps (s)'
    linechart.x_labels          = timelist
    linechart.x_labels_major_count = 20
    linechart.show_minor_x_labels = False
    for i in range(analogSensors):
        linechart.add('Pin {p}'.format(p = i), listValueLists[i])
    
    # We're creating a temp graph because pygal removes it when graph
    #   creation begins
    linechart.render_to_file(os.path.join(dataDir, graphTempName))
    # Graph to be linked
    os.rename(os.path.join(dataDir, graphTempName),
              os.path.join(dataDir, graphName))
    
    return 0
