#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'daysgrounded==0.0.17','console_scripts','daysgrounded'
__requires__ = 'daysgrounded==0.0.17'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('daysgrounded==0.0.17', 'console_scripts', 'daysgrounded')()
    )
