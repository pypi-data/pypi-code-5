# -*- coding: utf-8 -*-

"""
    fatafat.util
    ~~~~~~~~~~~~

    This module contains helper methods used in fatafat.

    :copyright: (c) 2014 by Subhajit Ghosh.
    :license: Apache2, see LICENSE for more details.
"""

import os


def create_parent_dir(path):
    """Creates the parent directory of a file if it does not exist."""
    parent_path = os.path.dirname(path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)


def rel_paths(directory, extensions=None):
    """Returns the relative paths of the files, sub-directories in a
    directory."""
    if not extensions:
        extensions = ['.md']

    for path, _, files in os.walk(directory):
        for name in files:
            if os.path.splitext(name)[1] in extensions:
                rel_dir = os.path.relpath(path, directory)
                yield os.path.join(rel_dir, name)


def makedir(directory):
    """Creates a directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)