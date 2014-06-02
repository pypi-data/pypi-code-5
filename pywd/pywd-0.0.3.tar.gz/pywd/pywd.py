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
from random import choice, sample

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
    while len(password) < length:
        if numbers and len(password) < length:
            password += choice(digits)
        if letters and len(password) < length:
            password += choice(ascii_lowercase)
        if symbols and len(password) < length:
            password += choice(punctuation)
        if uppercase and len(password) < length:
            password += choice(ascii_uppercase)
    return ''.join(sample(password, len(password)))
