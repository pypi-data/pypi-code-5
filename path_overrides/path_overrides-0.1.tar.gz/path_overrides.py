#!/usr/bin/env python
"""
Detect duplicate programs in the path

Ignores ones which are really the same (e.g. a symlink from one to another)

@codedstructure 2014
"""

import os
import itertools

__version__ = "0.1"
__author__ = "Ben Bass"


def path_diff():
    # map from entry in 'PATH' to the file listing for that path
    exes = {}

    path_spec = os.environ.get('PATH', '').split(':')
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
            left_exe = os.path.join(left, entry)
            right_exe = os.path.join(right, entry)
            try:
                # We need disk IO now, this could fail (e.g. dangling
                # symlinks, dodgy permissions, etc)
                if not (os.access(left_exe, os.X_OK) or
                        os.access(right_exe, os.X_OK)):
                    # ignore non-executable files
                    continue

                different = not os.path.samefile(left_exe, right_exe)
            except OSError as e:
                yield (left_exe, right_exe, e)

            if different:
                if os.path.islink(left_exe):
                    left_exe += " ({})".format(os.readlink(left_exe))
                if os.path.islink(right_exe):
                    right_exe += " ({})".format(os.readlink(right_exe))
                yield (left_exe, right_exe, None)


def main():
    try:
        from blessings import Terminal
    except ImportError:
        class Terminal(object):
            def identity(self, x):
                return x

            red = green = blue = identity

    T = Terminal()

    for left, right, err in path_diff():
        if err is None:
            print("{} overrides {}".format(T.green(left), T.blue(right)))
        else:
            print("Could not determine file differences ({}): {}, {}".format(
                T.red(err), T.green(left), T.blue(right)))


if __name__ == '__main__':
    main()
