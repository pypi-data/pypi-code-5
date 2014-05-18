#!/usr/bin/env python

"""
This module is recurlister.py. It contains a function called
print_lol, which takes a positional argument which may or may
not include be a nested list. 

For testing purposes this module can be executed from 
from the command line. A dummy nested list named movies is provided. 
"""

movies = [ 'The Holy Grail', 1975,
        'Terry Jones & Terry Gilliam', 91,
        ['Graham Chapman', ['Michael Palin', 'John Cleese',
        'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

def print_lol (theList):
    """
    print_lol () takes a positional argument called theList which may or 
    may not be a nested Python list. Each data item in the list is 
    recursively printed on a separate line. 
    """

    for item in theList:
        if isinstance(item,list):
            print_lol(item)
        else:
            print (item)


if __name__ == '__main__':

    print_lol(movies)
