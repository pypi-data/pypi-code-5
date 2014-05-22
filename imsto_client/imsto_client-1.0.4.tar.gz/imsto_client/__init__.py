from client import ImstoClient


VERSION = (1, 0, 4)


def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    return '.'.join(map(str, VERSION))

__version__ = get_version()
__author__ = 'Eagle Liut'
__author_email__ = 'liutao@liut.cc'
