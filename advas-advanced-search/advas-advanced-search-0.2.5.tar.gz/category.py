# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# AdvaS Advanced Search 0.2.5
# advanced search algorithms implemented as a python module
# category module
#
# (C) 2002 - 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email fh@efho.de
# -----------------------------------------------------------

class Category:

	def __init__(self):
		return

class Node:
	
	def__init__(self, nodeName):
		name = nodeName
		next = []
		up = []
		root = False
		
		return
			
	def isRootNode(self):
		"checks a node for being a root node"
		return self.root
		
	def isLeafNode(self):
		"checks a node for being a leaf node"
		if len(self.next) == 0:
			return True
		else:
			return False
