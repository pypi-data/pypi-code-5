#!python
# EASY-INSTALL-ENTRY-SCRIPT: 'technical-indicators==0.0.13','console_scripts','technical_indicators'
__requires__ = 'technical-indicators==0.0.13'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('technical-indicators==0.0.13', 'console_scripts', 'technical_indicators')()
    )
