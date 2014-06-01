#!/usr/bin/env python

"""
This module is recurlister.py. It contains a function called
print_lol, which takes a positional argument which may or may
not include be a nested list. 

For testing purposes this module can be executed from 
from the command line. A dummy nested list named movies is provided. 
The default parameters are tested to demonstrate the expected 
as described in the print_lol comments.
"""

movies = [ 'The Holy Grail', 1975,
        'Terry Jones & Terry Gilliam', 91,
        ['Graham Chapman', ['Michael Palin', 'John Cleese',
        'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

def print_lol (theList, indent = False, level=0):
    """
    print_lol () 
    Parameters: thelist:  a positional argument called which 
                          may or may not be a nested Python list. Each data 
                          item in the list is recursively printed on a separate                          line. 
                indent:   An optional boolen argument with a default value of 
                          False. False turns off indentation. True turns on
                          indentation. 
                Level:    Sets the number of tabs for the starting 
                          indentation level.   
                          
                          

    """

    for item in theList:
        if isinstance(item,list):
            print_lol(item, indent, level +1)
        else:
            if indent == True:
                for tab_stop in range(level):
                    print('\t'),

            print (item)


if __name__ == '__main__':

    print ("print_lol: with no optional parameters")
    print("==================================")
    print_lol(movies)
    for i in range(2):
        print("\n");
    

    print ("print_lol parameters: indent defaults to False, level = 2")
    print("==================================")
    print_lol(movies,level=2)
    for i in range(2):
        print("\n");

    print('print_lol parameters: indent = True, level = 2')  
    print("==================================")
    print_lol(movies,indent=True,level=2)
