#-------------------------------------------------------------------------------
# Name:        box_insertion.py
# Purpose:     The main file of the module
#
# Author:      Aadit
#
# Created:     23/05/2014
# Copyright:   (c) Aadit 2014
# Licence:     None
#-------------------------------------------------------------------------------

import box
import pickle
import box_variable
import sys
import checking
import error
box_data = []
logged_in= False
try:
    user = open("data.pkl","r")
    username= pickle.load(user)
    password = pickle.load(user)
except IOError:
    error.show("Cannot init file!\n")

user_data = [username,password]

def login(u,p):
    if u == (username) and p == (password):
        global logged_in
        logged_in = True
        print "Welcome {}." .format(username)
    else:
        error.show("Invalid login!\n")
        sys.exit(0)

def insert(*data):
    '''
        insert(...) -> list
        Add multiple items in the list
    '''
    if checking.check_login(logged_in):
        for i in range(len(data)):
            box_data.append(data)
    else:
        error.show("Plese login!\n")


def show():
    '''
        Shows the contents of the box
    '''
    if checking.check_login(logged_in):
        for item in range(len(box_data)):
            print "Item[%d]: %s\n" % (item,box_data(item))
    else:
        error.show("Plese login!\n")

def count(x):
    if x == int(x):
        error.show("INT type not allowed!\n")
    else:
       return  lambda : len(x)







