#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# xkcdpass
# http://danielmcgraw.github.io/xkcdpass/
#
# pyxkcdpass
# https://github.com/ikkebr/xkcdpass
#
# Generate passwords like Randall Munroe (http://xkcd.com/936/)
# Default dictionary from http://www.englishclub.com/vocabulary/common-words-5000.htm
#

from __future__ import print_function
import os
import random
from optparse import OptionParser


class XKCDPass(object):
    def __init__(self, dictionary='dictionary', length=4, *args, **kwargs):
        self.dictionary = dictionary
        self.length = length
        
    def generate_random_password(self, length=None):
        with open(self.dictionary, 'r') as dictionary:
            return " ".join( map(str.strip, random.sample(dictionary.readlines(), length or self.length)) )


def main(): # pragma: no cover
    usage = "pyxkcdpass.py [-h|--help] [-l|--length=<length>] [-d|--dictionary=<path>]"

    parser = OptionParser(usage=usage)

    default_dictionary = os.path.join(os.path.dirname(__file__), 'dictionary')
    print(default_dictionary)
    
    parser.add_option("-d", "--dictionary", dest="dictionary_path",
                      help="Specify a path to a dictionary", metavar="PATH", default=default_dictionary)

    parser.add_option("-l", "--length", dest="password_length", type="int",
                      help="Specify the password length", metavar="LENGTH", default=4)


    (options, args) = parser.parse_args()

    if options.password_length < 1:
        parser.error("Your password should contain at least 1 word.")

    if not os.path.isfile(options.dictionary_path):
        parser.error("I cannot find your dictionary file. Please make sure it is readable.")

    xkcdpass = XKCDPass(options.dictionary_path, options.password_length)
    
    print(xkcdpass.generate_random_password())
    



if __name__ == "__main__": # pragma: no cover
    main()
