"""
This file contains the routine 'loadyaml' that is used to load YAML files containing Table and View
definitions.  
"""
# stdlib
from __future__ import absolute_import    # needed since this file is called 'yaml' and importing yaml
import yaml
import os.path

# local module
from .loader import RunstatLoader 

__all__ = ['loadyaml']

def loadyaml( path ):
  """
  Load a YAML file at :path: that contains Table and View definitions.
  Returns a <dict> of item-name anditem-class definition.  

  If you want to import these definitions directly into your namespace, (like a module)
  you would do the following:

    globals().update( loadyaml( <path-to-yaml-file> ))

  If you did not want to do this, you can access the items as the <dict>.  For 
  example, if your YAML file contained a Table called MyTable, then you could do
  something like:

    catalog = loadyaml( <path-to-yaml-file> )
    MyTable = catalog['MyTable']

    table = MyTable(dev)
    table.get()
    ...
  """
  # if no extension is given, default to '.yml'
  if os.path.splitext(path)[1] == '': path += '.yml'  
  return RunstatLoader().load( yaml.load( open(path, 'r' )))