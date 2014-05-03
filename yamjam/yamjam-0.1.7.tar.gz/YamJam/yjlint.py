'''yamjam config linter helper script'''
# py3 compatibility
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from YamJam import yamjam, YAMLError

import os
import pprint
import sys


def print_contents(fname, retcode):
    '''output contents of file, exist with code, retcode'''
    print('**** File Contents ****')
    print(open(fname).read())
    print('**** END Contents  ****')
    print("ERROR - yjlint halted")
    sys.exit(retcode)


def lint_yamjam(argz, plain=False):
    '''attempt to read configs with yamjam, capturing and humanizing errors'''
    if plain:
        prtfn = print
    else:
        prtprn = pprint.PrettyPrinter()
        prtfn = prtprn.pprint

    for pth in argz.split(';'):
        if os.path.exists(os.path.expanduser(pth)) == False:
            print('Warning: %s  Not Found.' % pth)
        else:
            print('config: %s' % pth)
            try:
                cfg = yamjam(pth)
            except TypeError:
                print('ERROR: yaml does not evaluate to a dictionary')
                print_contents(pth, 1)
            except YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    print("Error position: (%s:%s)" % (mark.line+1,
                                                       mark.column+1))
                    print_contents(pth, 2)
                else:
                    print("Error in configuration file: %s" % exc)
                    print_contents(pth, 3)

            prtfn(cfg)
            print('Confirmed: Valid YAML')


def display_help(retcode=0):
    '''print help'''
    usage = "Usage:\n"
    usage += "\tyjlint [options] config_file\n"
    usage += "\n"
    usage += "where config_file specifies path and name of file, most likely, ~/.yamjam/config.yaml\n"
    usage += "[options]\n"
    usage += "-h --help ::   display help\n"
    print(usage)
    sys.exit(retcode)


def main():
    '''main function used as an entry point for the console script'''
    sysargs = list(sys.argv)

    if '-h' in sysargs:
        display_help(0)
    if '--help' in sysargs:
        display_help(0)

    plain = False
    if '--plain' in sysargs:
        plain = True
        del sysargs[sysargs.index('--plain')]

    if len(sysargs) < 2:
        display_help(0)
    elif len(sysargs) == 2:
        args = sysargs[-1]
    else:
        args = ';'.join(sysargs[1:])

    lint_yamjam(args, plain=plain)

if __name__ == '__main__':
    main()
