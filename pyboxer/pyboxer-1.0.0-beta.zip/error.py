#-------------------------------------------------------------------------------
# Name:       error.py
# Purpose:    The errors file
#
# Author:      Aadit
#
# Created:     22/05/2014
# Copyright:   (c) Aadit 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys

def show(msg):
        print "ERROR: ",
        sys.stderr.write(msg)


