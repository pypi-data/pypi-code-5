# vim: set et ts=4 sw=4 fileencoding=utf-8:
'''
pycsync.cli
===========

Module for command line script functions (aka a place for main).
'''

from os.path import curdir
import argparse

from pycsync import version, auth, sync


def pycsync_main():
    '''
    Main function for pycsync script. It handels parsing command line args
    and calling the functions to preform syncing.
    '''
    parser = argparse.ArgumentParser(description='Sync pictures with Flickr.')
    parser.add_argument('-p', '--path',
                        default=None,
                        help='Root directory to sync. Defaults to cwd.')
    parser.add_argument('-a', '--auth',
                        action='store_true',
                        default=False,
                        help='Request authorization token')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        default=False,
                        help='Display pycsync version')
    args = parser.parse_args()

    if args.path is None:
        args.path = curdir
    if args.version:
        print version.__version__
    elif args.auth:
        auth.request_token(args.path)
    else:
        sync.sync(args.path)
