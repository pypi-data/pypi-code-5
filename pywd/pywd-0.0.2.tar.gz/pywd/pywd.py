"""
Usage:
    pywd --length=<len> [--numbers] [--letters] [--symbols]
         [-u | --uppercase]
    pywd -v | --version
    pywd -h | --help

Examples:
    pywd --length=14 --numbers --symbols
    pywd --length=10 --symbols
    pywd --length=10 --letters --numbers

Options:
    -h --help       Show this screen.
    -v --version    Show version.
"""

from docopt import docopt
from pywd import __version__
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from random import choice, getrandbits
try:
    from __future__ import print_function
except ImportError:
    pass


def generate():
    version = ".".join(str(x) for x in __version__)
    arguments = docopt(__doc__, version=version)
    length = int(arguments.get("--length"))
    numbers = arguments.get("--numbers")
    letters = arguments.get("--letters")
    symbols = arguments.get("--symbols")
    uppercase = arguments.get("--uppercase")
    print(create_password(length, numbers, letters, symbols, uppercase))


def create_password(length, numbers, letters, symbols, uppercase):
    password = ""
    if numbers and not any([letters, symbols, uppercase]):
        for x in range(0, length):
            password += choice(digits)
    elif all([numbers, letters]) and not any([symbols, uppercase]):
        for x in range(0, length):
            if bool(getrandbits(1)):
                password += choice(digits)
            else:
                password += choice(ascii_lowercase)
    elif all([numbers, symbols]) and not any([letters, uppercase]):
        for x in range(0, length):
            if bool(getrandbits(1)):
                password += choice(digits)
            else:
                password += choice(punctuation)
    elif all([numbers, symbols, letters]) and not uppercase:
        for x in range(0, length):
            selection = choice([1, 2, 3])
            if selection == 1:
                password += choice(digits)
            elif selection == 2:
                password += choice(ascii_lowercase)
            elif selection == 3:
                password += choice(punctuation)
    elif all([numbers, letters, uppercase]) and not symbols:
        for x in range(0, length):
            selection = choice([1, 2, 3])
            if selection == 1:
                password += choice(digits)
            elif selection == 2:
                password += choice(ascii_lowercase)
            elif selection == 3:
                password += choice(ascii_uppercase)
    elif letters and not any([symbols, uppercase, numbers]):
        for x in range(0, length):
            password += choice(ascii_lowercase)
    elif all([letters, symbols]) and not any([numbers, uppercase]):
        for x in range(0, length):
            if bool(getrandbits(1)):
                password += choice(ascii_lowercase)
            else:
                password += choice(punctuation)
    elif all([letters, uppercase]) and not any([numbers, symbols]):
        for x in range(0, length):
            if bool(getrandbits(1)):
                password += choice(ascii_uppercase)
            else:
                password += choice(ascii_lowercase)
    elif all([letters, uppercase, symbols]) and not numbers:
        for x in range(0, length):
            selection = choice([1, 2, 3])
            if selection == 1:
                password += choice(ascii_lowercase)
            elif selection == 2:
                password += choice(ascii_uppercase)
            elif selection == 3:
                password += choice(punctuation)
    elif symbols and not any([letters, numbers, uppercase]):
        for x in range(0, length):
            password += choice(punctuation)
    elif all([numbers, letters, symbols, uppercase]):
        for x in range(0, length):
            selection = choice([1, 2, 3, 4])
            if selection == 1:
                password += choice(digits)
            elif selection == 2:
                password += choice(ascii_lowercase)
            elif selection == 3:
                password += choice(punctuation)
            else:
                password += choice(ascii_uppercase)
    else:
        raise Exception("The combination you requested is not available!")
    return password
