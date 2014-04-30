"""rw

Generate random words.

Usage:
  rw [--dict=<wordfile>] [-s | --secure] <numberofwords>
  rw (-h | --help)
  rw --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  -s --secure           Use cryptography-strength random numbers
  --dict=<wordfile>     Use given word file (optional).

"""
from __future__ import print_function

import random
import io

import six
import docopt
import pkg_resources

__VERSION__ = '0.0.2'

def generate_words(numberofwords, wordlist, secure=None):
    """Generate a list of random words from wordlist."""
    if not secure:
        chooser = random.choice
    else:
        chooser = random.SystemRandom().choice
    return [chooser(wordlist) for _ in range(numberofwords)]

def read_wordlist(dictfile):
    """Read a wordlist from file (one word per line)."""
    return [line.strip() for line in dictfile.readlines()]

def load_stream(filename):
    """Load a file stream from the package resources."""
    rawfile = pkg_resources.resource_stream(__name__, filename)
    if six.PY2:
        return rawfile
    return io.TextIOWrapper(rawfile, 'utf-8')

def cli():
    """Run the command line interface."""
    args = docopt.docopt(__doc__, version=__VERSION__)
    secure = args['--secure']
    numberofwords = int(args['<numberofwords>'])

    dictpath = args['--dict']
    if dictpath is not None:
        dictfile = open(dictpath)
    else:
        dictfile = load_stream('words.txt')
    with dictfile:
        wordlist = read_wordlist(dictfile)

    words = generate_words(numberofwords, wordlist, secure=secure)
    print(' '.join(words))
