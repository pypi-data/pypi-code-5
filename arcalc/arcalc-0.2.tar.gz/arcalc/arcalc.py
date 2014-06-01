#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import os
import sys

__appname__ = 'A/R Calculator'
__version__ = "v.0.2"

def welcome():
	print"""
 	                     o
	                o    |
	                 \   |
	                  \  |
	                   \.|-.
	                   (\|  )
	          .==================.
	          | .--------------. |
	          | |--.__.--.__.--| |
	          | |--.__.--.__.--| |
	          | |--.__.--.__.--| |
	          | |--.__.--.__.--| |   ,--,
	          | |--.__.--.__.--| |   |o.|
	          | '--------------'o|   |::|
	          |  '''            o|   |::|
	          '=================='   '--'
	
	           %s %s\n""" % (__appname__, __version__)

def calculate():
	ori_width = raw_input("Please enter the original width: ")
	ori_height = raw_input("Please enter the original height: ")
	new_width = raw_input("Please enter the desired width: ")
	
	new_height = int(ori_height) / int(ori_width) * int(new_width)
	print "\nYour desired resolution is: " + new_width + " x %.0f" % new_height
	
	aspect_ratio = int(new_width) / int(new_height)
	
	print "The resulting A/R is: " + str(aspect_ratio)[:4] + ":1"
	
def main():
	try:
		welcome()
		calculate()
	except KeyboardInterrupt:
		os.system("clear")
		sys.exit(0)
	
if __name__ == '__main__':
	main()
