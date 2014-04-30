#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from argparse import ArgumentParser
from copy import deepcopy
from glob import glob
from threading import Thread, active_count
from time import sleep
import sys

import requests

from . import __version__


def parse_html(html):
    return html.splitlines()


def upload(f):
    url = 'http://www.bild.me/index.php'
    data = {
        't': 1,
        'C1': 'ON',
        'upload': 1,
    }
    files = {
        'F1': f
    }
    try:
        html = requests.post(url, data=data, files=files).text
        return {'status': 0, 'result': parse_html(html)}
    except requests.exceptions:
        return {'status': 1, 'message': 'Upload failed!'}
    except Exception as e:
        return {'status': 1, 'message': e}


def output_result(result, list_all):
    if result['status'] == 1:
        sys.stderr.write(result['message'] + '\n')
    if list_all:
        print('\n\n'.join(result['result']))
    else:
        print(result['result'][5])


class ProgressBar(object):
    def __init__(self, list_all, show=True):
        self.progress = {}
        self.list_all = list_all
        self.show = show

    def output(self, name, n, size):
        s = '{0}: [{1}]\r'.format(name, ('=' * n + '>').ljust(size))
        sys.stdout.write(s)
        sys.stdout.flush()

    def run(self):
        size = 50
        for x in range(1, size + 1):
            for (k, p) in deepcopy(self.progress).items():
                _x = x
                if p['finish']:
                    _x = size
                if self.show:
                    self.output(k, _x, size)

                if p['finish']:
                    if self.show:
                        print('')
                    result = p['result']
                    output_result(result, self.list_all)
                    del self.progress[k]
                    continue

                sleep(0.3)

            if not self.progress:
                break


class UploadThread(Thread):
    def __init__(self, img, bar, *args, **kwargs):
        self.img = img
        self.bar = bar
        super(UploadThread, self).__init__(*args, **kwargs)

    def run(self):
        with open(self.img, 'rb') as f:
            self.bar.progress[f.name] = {'finish': False}
            result = upload(f)
            self.bar.progress[f.name]['finish'] = True
            self.bar.progress[f.name]['result'] = result


def main():
    parser = ArgumentParser(description='CLI tool for bild.me.')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-l', '--list', action='store_true',
                        help='list all result')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='decrease verbosity')
    parser.add_argument('-f', '-F', '--file', required=True,
                        nargs='+', help=('picture file path, '
                                         'support Unix shell-style wildcards'
                                         )
                        )
    args = parser.parse_args()

    file_args = set(args.file)
    files = []
    for x in file_args:
        files.extend(glob(x))

    list_all = args.list
    show = not args.quiet
    bar = ProgressBar(list_all, show)

    for n, img in enumerate(files):
        t = UploadThread(img, bar)
        t.start()

    while True:
        n = active_count()
        if n == len(files):
            bar.run()
            break

if __name__ == '__main__':
    main()
