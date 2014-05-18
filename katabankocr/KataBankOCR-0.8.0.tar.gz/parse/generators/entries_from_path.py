"generator that yields Entries"

import fileinput

from toolz import partition_all

from parse import settings

def entries_from_path(path):
    "generator that yields Entries either from Path or from StdIn"
    return partition_all(settings.lines_per_entry, _lines_from_path(path))

def _lines_from_path(path):
    "generator that yields Lines either from Path or from StdIn"
    for line in fileinput.input(path):
        yield str(line).rstrip('\n')
