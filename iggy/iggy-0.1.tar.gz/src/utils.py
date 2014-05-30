# Copyright (c) 2014, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of iggy.
#
# iggy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iggy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iggy.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import os

#some pretty printers for predictions, minimal inconsistent cores, etc

def print_predictions(predictions) :
    predictions = sorted(predictions, key=lambda p: str(p.arg(0)))
    exp = ''
    pred_plus = set()
    pred_minus = set()
    pred_nochange = set()
    pred_not_plus = set()
    pred_not_minus = set()
    pred_change = set()
    for p in predictions:
      if p.pred() == "pred_plus" :
	pred_plus.add(p.arg(1))
      if p.pred() == "pred_minus" :
	pred_minus.add(p.arg(1))
      if p.pred() == "pred_nochange" :
	pred_nochange.add(p.arg(1))
      if p.pred() == "pred_not_plus" :
	pred_not_plus.add(p.arg(1))
      if p.pred() == "pred_not_minus" :
	pred_not_minus.add(p.arg(1))
      if p.pred() == "pred_change" :
	pred_change.add(p.arg(1))

    pred_not_plus.difference_update(pred_minus)
    pred_not_plus.difference_update(pred_nochange)
    pred_not_minus.difference_update(pred_plus)
    pred_not_minus.difference_update(pred_nochange)
    pred_change.difference_update(pred_minus)
    pred_change.difference_update(pred_plus)
    for p in pred_plus : print('   '+str(p)+ ' = + ')
    for p in pred_minus : print('   '+str(p)+ ' = - ')
    for p in pred_nochange : print('   '+str(p)+ ' = 0 ')
    for p in pred_not_plus : print('   '+str(p)+ ' = NOT + ')
    for p in pred_not_minus : print('   '+str(p)+ ' = NOT - ')
    for p in pred_change : print('   '+str(p)+ ' = CHANGE ')

def print_coloring(colorings) :
    labels = set()
    repairs = set()
    for c in colorings:
      if c.pred() == "vlabel" :
	labels.add(c)
      if c.pred() == "err" :
	repairs.add(c)
      if c.pred() == "rep" :
	repairs.add(c)
    for c in labels :
      print '   ',c.arg(1),'=',c.arg(2)
    for c in repairs :
      print '   ',c.arg(0)
                  
def print_mic(mic, net, obs):
  
    nodes = []
    edges = []
    for node in mic: nodes.append(str(node.arg(1)))
    
    predecessors = []
    for e in net:
       if e.pred() == "obs_elabel" :
          #print str(e)
          #print str(e.arg(0)),str(e.arg(1)),str(e.arg(2))
          if str(e.arg(1)) in nodes : 
            predecessors.append(str(e.arg(0)))
            if str(e.arg(2)) == "1" : edges.append( str(e.arg(0))+ " -> " + str(e.arg(1))+ " +")
            if str(e.arg(2)) == "-1" : edges.append(str(e.arg(0))+ " -> " + str(e.arg(1))+ " -")
         #TODO ? edges
    for edge in edges: print('   '+edge)
    for o in obs:
       if o.pred() == "obs_vlabel" :  
          if str(o.arg(1)) in nodes :
              if str(o.arg(2))=="1" :  print '   '+str(o.arg(1))+ " = +"
              if str(o.arg(2))=="-1" :  print '   '+str(o.arg(1))+ " = -"
          if str(o.arg(1)) in predecessors :
              if str(o.arg(2))=="1" :  print '   '+str(o.arg(1))+ " = +"
              if str(o.arg(2))=="-1" :  print '   '+str(o.arg(1))+ " = -"
    

def clean_up() :
  if os.path.isfile("parser.out"): os.remove("parser.out")
  if os.path.isfile("asp_py_lextab.py"): os.remove("asp_py_lextab.py")
  if os.path.isfile("asp_py_lextab.pyc"): os.remove("asp_py_lextab.pyc")
  if os.path.isfile("asp_py_parsetab.py"): os.remove("asp_py_parsetab.py")
  if os.path.isfile("asp_py_parsetab.pyc"): os.remove("asp_py_parsetab.pyc") 
  if os.path.isfile("graph_parser_lextab.py"): os.remove("graph_parser_lextab.py")
  if os.path.isfile("graph_parser_parsetab.py"): os.remove("graph_parser_parsetab.py")
  if os.path.isfile("parsetab.py"): os.remove("parsetab.py")
  if os.path.isfile("parsetab.pyc"): os.remove("parsetab.pyc")
  if os.path.isfile("sif_parser_lextab.py"): os.remove("sif_parser_lextab.py")
  if os.path.isfile("sif_parser_lextab.pyc"): os.remove("sif_parser_lextab.pyc")
