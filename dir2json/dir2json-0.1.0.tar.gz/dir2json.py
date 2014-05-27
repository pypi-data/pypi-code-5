#!/usr/bin/env python3

import json
import os
import sys
import mimetypes

PRETTY_JSON = {'indent': 4}


def create_index(path, scanner):
    '''Creates a index structure given a os.walk like iterator'''

    lookup = {}
    plen = len(path)

    def directory(p):
        data = {
            'path': p[plen:],
            'type': 'directory',
            'index': []
        }
        # Add index to lookup with full path
        lookup[p] = data['index']
        return data

    def file(p):
        mime, enc = mimetypes.guess_type(p)

        data = {
            'path': p[plen:],
            'type': mime or 'unknown'
        }

        # If this file is a symlink resolve it and populate the link attribute
        try:
            rel = os.readlink(p)
        except OSError:
            pass
        else:
            link = os.path.relpath(os.path.join(os.path.dirname(p), rel), path)
            data['link'] = link

        return data

    tree = directory(path)

    for root, dirs, files in scanner:
        index = lookup.pop(root)

        for d in dirs:
            index.append(directory(os.path.join(root, d)))

        for f in files:
            index.append(file(os.path.join(root, f)))
            
    return tree


def nodot(l):
    '''Filter items that have a leading dot'''
    return [x for x in l if not x.startswith('.')]


def scan_directory(path, all=False):
    '''Wrapper around os.walk that optionally filters hidden directories
       and files
    '''

    walk = os.walk(path)
    if all:
        yield from walk
    else:
        for root, dirs, files in os.walk(path):
            dirs[:] = nodot(dirs)
            files = nodot(files)
            yield (root, dirs, files)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dir',
                        help="directory to create index of")
    parser.add_argument('--pretty',
                        action='store_true',
                        help="output pretty printed json")
    parser.add_argument('--all', '-a',
                        action='store_true',
                        help="include all files, even hidden")
    args = parser.parse_args()

    path = args.dir
    if not path.endswith('/'):
        path += '/'

    tree = create_index(path, scan_directory(path, args.all))

    jsonopts = PRETTY_JSON if args.pretty else {}
    json.dump(tree, sys.stdout, **jsonopts)


if __name__ == '__main__':
    main()
