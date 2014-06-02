#!/usr/bin/env python
"""
Detect duplicate programs in the path

Ignores ones which are really the same (e.g. a symlink from one to another)

@codedstructure 2014
"""

import os
import itertools

__version__ = "0.1.2"
__author__ = "Ben Bass"

identity = lambda x: x


class ExeInfo(object):
    path = None
    stat = None
    is_exec = None
    target = None
    error = None

    def __init__(self, path):
        self.path = path
        try:
            self.stat = os.stat(path)
            self.is_exec = os.access(path, os.X_OK)
        except OSError as e:
            self.error = str(e)
        if os.path.islink(path):
            self.target = os.readlink(path)

    def matches(self, other):
        if self.stat == other.stat:  # e.g. both None
            return True
        if self.stat is None or other.stat is None:
            return False
        return os.path.samestat(self.stat, other.stat)

    def render(self, default_format=None, link_format=None, error_format=None):
        default_format = default_format or identity
        link_format = link_format or identity
        error_format = error_format or identity

        result = self.path
        if self.target:
            result += ' ' + link_format('({})'.format(self.target))
        if self.error:
            result += ' ' + error_format('({})'.format(self.error))

        return default_format(result)

    def __str__(self):
        return self.render()


def path_diff():
    # map from entry in 'PATH' to the file listing for that path
    exes = {}

    path_spec = os.environ.get('PATH', '').split(os.pathsep)
    for path in path_spec[:]:
        try:
            # Note we could filter on only executable things here, but that
            # would require additional IO; doing (CPU-bound) string
            # manipulation first and only IO if required is (probably?) faster
            exes[path] = set(os.listdir(path))
        except OSError:
            # Perhaps the PATH entry doesn't refer to a valid directory
            path_spec.remove(path)

    for left, right in itertools.combinations(path_spec, 2):
        # 'left' will always be earlier in the path since path_spec is
        # sorted and combinations preserves this
        overlap = exes[left] & exes[right]
        for entry in overlap:
            left_info = ExeInfo(os.path.join(left, entry))
            right_info = ExeInfo(os.path.join(right, entry))

            if not (left_info.is_exec or right_info.is_exec):
                # ignore non-executable files
                continue

            if not left_info.matches(right_info):
                yield (left_info, right_info)


def main():
    try:
        from blessings import Terminal
    except ImportError:
        class Terminal(object):
            def __getattr__(self, key):
                return identity

    T = Terminal()

    for left, right in path_diff():
        print("{} overrides {}".format(left.render(T.bright_cyan, T.cyan, T.red),
                                       right.render(T.bright_blue, T.blue, T.red)))


if __name__ == '__main__':
    main()
