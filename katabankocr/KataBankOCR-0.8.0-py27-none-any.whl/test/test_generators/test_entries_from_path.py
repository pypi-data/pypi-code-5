"test the entries_from_path generator"

import pytest
from toolz import count, pipe

from parse.generators.entries_from_path import entries_from_path

from fixture_methods import Paths, Entries


path = Paths.basic_input_file()
entries = Entries.of_basic_input_file()

def test_with_bad_path():
    "confirm a bad path raises an expected error"
    iterator = entries_from_path('bad_path_string')
    pytest.raises((OSError, IOError,), tuple, iterator)

def test_line_count_of_known_input():
    "confirm all Lines read from basic input file"
    expected_entry_count = count(entries)
    found_entry_count = pipe(path, entries_from_path, count)
    assert expected_entry_count == found_entry_count

def test_known_lines_grouped_to_known_entries():
    "confirm known lines grouped into known entries"
    found_entries = entries_from_path(path)
    assert tuple(entries) == tuple(found_entries)
