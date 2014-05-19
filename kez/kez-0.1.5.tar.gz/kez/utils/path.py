
import os

__all__ = [
    'ensure_dir',
    'ensure_parent_dir',
]

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    elif not os.path.isdir(path):
        raise OSError("'%s' exists and is not a directory")

def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    ensure_dir(parent)
    return parent

