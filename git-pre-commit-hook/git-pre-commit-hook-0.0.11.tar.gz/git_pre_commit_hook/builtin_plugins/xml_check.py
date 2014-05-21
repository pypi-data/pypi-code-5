"""Check that files contains valid XML."""
from __future__ import print_function
import sys
from xml.etree import ElementTree


DEFAULTS = {
    'files': '*.xml',
}


def check(file_staged_for_commit, options):
    if not file_staged_for_commit.is_fnmatch(options.xml_files):
        return True
    try:
        ElementTree.fromstring(file_staged_for_commit.contents)
        return True
    except ElementTree.ParseError as e:
        print(e, file=sys.stderr)
        return False
