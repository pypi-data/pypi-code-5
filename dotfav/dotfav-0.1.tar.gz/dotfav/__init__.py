# -*- coding: utf-8 -*-

import sys


__version__ = '0.1'


def main(argv=sys.argv):
    from dotfav.cmdline import DotFav
    try:
        DotFav(argv).run()
        return 0
    except KeyboardInterrupt:
        return 1
