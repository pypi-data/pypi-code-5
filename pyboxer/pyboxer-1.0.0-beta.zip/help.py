#-------------------------------------------------------------------------------
# Name:        help.py
# Purpose:      Help file for the module
#
# Author:      Aadit
#
# Created:     22/05/2014
# Copyright:   (c) Aadit 2014
#-------------------------------------------------------------------------------
help_msg = {'default':"This is the help page",'version':"1.0.0.0","about":"(C) Aadit Kapoor 2014"}
def show(topic = 'default'):
    '''
        show(topic) -> str
    '''
    if topic == 'version':
        print "Help[2]: %s\n"% help_msg['version']
    elif topic == "about":
        print "Help[3]: %s\n"% help_msg['about']



