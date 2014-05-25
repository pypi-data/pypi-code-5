#-------------------------------------------------------------------------------
# Name:        Welcome
# Purpose:     Defines the start of the module, contains functions like copyright() etc.
#
# Author:      Aadit Kapoor
#
# Created:     22/05/2014
# Copyright:   (c) Aadit Kapoor 2014
# Licence:     GNU Public License
#-------------------------------------------------------------------------------
import pickle
import sys
import error
import help
#---------------------
def copyright_box():
    '''
        copyright_box() -> str
        Shows the copyright message of the program
    '''
    print "(C) Aadit Kapoor 2014\n"
    print "Version: [1.0.0.0]\n"
    print "Build [1000]\n"
#-------------------
def write_to_file(username_box = None,password_box = None):
    data_box = (username_box,password_box)
    data = open("data.pkl","w")
    for i in range(len(data_box)):
        pickle.dump(data_box[i],data)
    data.close()

#-------------------


