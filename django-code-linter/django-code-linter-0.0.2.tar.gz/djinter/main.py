# -*- coding: utf-8 -*-
import argparse
import sys

from djinter import __version__
from djinter.lint import lint_project


def main(prog=None):
    parser = argparse.ArgumentParser(prog=prog, version=__version__)
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()

    results = []

    for path in args.paths:
        results.extend(lint_project(path))
    for result in results:
        if result.get('severity') == 'critical':
            sys.stderr.write('%s\n' % result['message'])
            exit_code = 101
    sys.exit(exit_code)
