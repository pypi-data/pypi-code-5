#-------------------------------------------------------------------------------
# Name:        box.py
# Purpose:     Extension for box_insertion.py
#
# Author:      Aadit
#
# Created:     23/05/2014
# Copyright:   (c) Aadit 2014
#-------------------------------------------------------------------------------
import welcome
import box_variable
import checking
import box_insertion as function
box_id = box_variable.box_code
welcome.copyright_box()
def init_box(username_box,password_box):
    box_variable.username = username_box
    box_variable.password = password_box

def check_box():
    if checking.check_data(box_variable.username,box_variable.password):
        print "Please Provide Data!\n"
    else:

        print "Box's Name: ",box_variable.username
        print "Box's Password: ", box_variable.password
        print "Box Code ", box_id
        print "\n"
        print "Are you sure this is the information (y/n)"
        c = raw_input()
        if c == 'y':
            box_variable.check = True
            box_variable.box_created = True
        else:
            print "Creation Failed, Please try again!"
            welcome.sys.exit(0)

def finalize_box():
    if box_variable.check == True:
        welcome.write_to_file(box_variable.username,box_variable.password)






