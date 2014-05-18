"methods that provide values for testing and an interface to constants"

import os
import copy
import random

from toolz import pipe, curry
from toolz.curried import nth
from toolz.curried import map as cmap

from parse import settings
import parse

from common_tools import get_one_or_more, adulterate_iterable, bad_length_duplicator
import fixture_constants

_first_elements = cmap(curry(nth, 0))
_second_elements = cmap(curry(nth, 1))
_third_elements = cmap(curry(nth, 2))
_fourth_elements = cmap(curry(nth, 3))
_fifth_elements = cmap(curry(nth, 4))

class Numerals:
    "methods that provide Numerals for testing"

    @classmethod
    def get_random(cls, count=None):
        "return random valid Numeral[s]"
        getter = lambda: random.choice(cls.valid())
        return get_one_or_more(getter, count)

    @staticmethod
    def valid():
        "return ordered tuple of valid Numerals"
        return pipe(settings.valid_numerals, sorted, tuple)

    @classmethod
    def invalid(cls):
        "return tuple of arbitrary basestrings that includes no valid numerals"
        chars = ArbitraryValues.single_character_basestrings()
        not_valid = lambda value: value not in cls.valid()
        limit_to_invalid = curry(filter, not_valid)
        return pipe(chars, limit_to_invalid, tuple)

class Accounts:
    "methods that provide Accounts for testing"

    @staticmethod
    def get_random(count=None):
        "return random Account[s]"
        getter = lambda: ''.join(Numerals.get_random(settings.figures_per_entry))
        return get_one_or_more(getter, count)

    @staticmethod
    def of_example_accounts():
        "return Accounts from superpositions of example Accounts"
        return _second_elements(fixture_constants.example_accounts)

    @staticmethod
    def of_basic_input_file():
        "return Accounts from basic input file"
        return fixture_constants.BasicInputFile.accounts

    @staticmethod
    def of_flawed_accounts():
        "return [in]valid Accounts from Superpositions with flaws"
        return _fourth_elements(fixture_constants.flawed_accounts)

class Figures:
    "methods that provide Figures for testing"

    @staticmethod
    def get_random(count=None):
        "return random valid Figure[s]"
        getter = lambda: random.choice(settings.figures.keys())
        return get_one_or_more(getter, count)

    @staticmethod
    def from_numeral(numeral):
        "return the Figure that represents the given Numeral"
        return settings.figures.keys()[settings.figures.values().index(numeral)]

    @classmethod
    def from_account(cls, account):
        "return the Figures that represent the given Account"
        return pipe(account, tuple, cmap(cls.from_numeral), tuple)

    @classmethod
    def valid(cls):
        "return ordered Figures representing Numerals 0-9"
        return cmap(cls.from_numeral, Numerals.valid())

    @staticmethod
    def flawed():
        "return flawed Figures from fixture_constants"
        return pipe(fixture_constants.flawed_figures, _first_elements)

class Strokes:
    "methods that provide Strokes for testing"

    @classmethod
    def get_random(cls, count=None):
        "return random valid Stroke[s]"
        getter = lambda: random.choice(cls.valid())
        return get_one_or_more(getter, count)

    @staticmethod
    def valid():
        "return ordered tuple of valid Strokes"
        return pipe(settings.valid_strokes, sorted, tuple)

    @classmethod
    def invalid(cls):
        "return tuple of arbitrary single-char basestrings with 0 valid strokes"
        chars = ArbitraryValues.single_character_basestrings()
        not_valid = lambda value: value not in cls.valid()
        limit_to_invalid = curry(filter, not_valid)
        return pipe(chars, limit_to_invalid, tuple)

class Lines:
    "methods that provide Lines for testing"

    @staticmethod
    def get_random(count=None):
        "return random Lines[s] composed of Strokes"
        return pipe(settings.strokes_per_line, Strokes.get_random, ''.join)

    @staticmethod
    def of_invalid_types():
        "return arbitrary values that do not include any basestrings"
        return ArbitraryValues.non_basestrings()

    @classmethod
    def of_invalid_lengths(cls):
        "return Lines of invalid length"
        return bad_length_duplicator(cls.get_random())

    @classmethod
    def with_invalid_strokes(cls):
        "return tuple of Lines that each include an invalid stroke"
        return pipe(Strokes.invalid(), cmap(cls._by_invalid_stroke), tuple)

    @classmethod
    def _by_invalid_stroke(cls, invalid_stroke):
        "return a Line that includes an invalid stroke"
        return adulterate_iterable(cls.get_random(), invalid_stroke)

class Entries:
    "methods that provide Entries for testing"

    @classmethod
    def get_random(cls, count=None):
        "return one or more random Entries"
        getter = lambda: cls.from_account(Accounts.get_random())
        return get_one_or_more(getter, count)

    @classmethod
    def from_account(cls, account):
        "return the Entry (tuple of Lines) that represents the given Account"
        return pipe(account, Figures.from_account, cls.from_figures)

    @classmethod
    def from_figures(cls, figures):
        "return the Entry (tuple of Lines) that contains the given Figures"
        lines = cmap(curry(cls._line_by_index, figures))
        return pipe(settings.lines_per_entry, range, lines, tuple)

    @classmethod
    def _line_by_index(cls, figures, line_index):
        "return a Line composed of Figures Substrings"
        substrings = cmap(curry(cls._substring_by_index, line_index))
        return pipe(figures, substrings, ''.join)

    @staticmethod
    def _substring_by_index(line_index, figure):
        "return Substring of Figure by Entry Line index"
        start_index = line_index * settings.strokes_per_substring
        end_index = start_index + settings.strokes_per_substring
        return figure[start_index:end_index]

    @classmethod
    def of_basic_input_file(cls):
        "return Entries from basic input file"
        return pipe(Accounts.of_basic_input_file(), cmap(cls.from_account), tuple)

class Superpositions:
    "methods that provide Superpositions for testing"

    @classmethod
    def from_numeral(cls, numeral):
        "return Superposition of Figure representing Numeral"
        return cls.of_valid_figures()[Numerals.valid().index(numeral)]

    @classmethod
    def from_account(cls, account):
        "return list of Superpositions from Figures in Account's Numerals"
        return map(cls.from_numeral, account)

    @staticmethod
    def of_valid_figures():
        "return tuple of Superpositions for all un-flawed Figures"
        return copy.deepcopy(fixture_constants.valid_figure_superpositions)

    @classmethod
    def of_example_accounts(cls):
        "return lists of Superpositions made from example accounts"
        return pipe(fixture_constants.example_accounts, _first_elements, cmap(cls.from_account))

    @staticmethod
    def of_flawed_figures():
        "return tuple of Superpositions of flawed figures"
        return pipe(fixture_constants.flawed_figures, _second_elements, tuple)

    @classmethod
    def of_flawed_accounts(cls):
        "return tuple of Superpositions of Accounts including flawed figures"
        superpositions = lambda indexes: (cls._by_flawed_figure_index(i) for i in indexes)
        return pipe(fixture_constants.flawed_accounts, len, range, superpositions, tuple)

    @classmethod
    def _by_flawed_figure_index(cls, flawed_figure_index):
        "return Superpositions of an Account including a flawed figure"
        flawed_account = fixture_constants.flawed_accounts[flawed_figure_index]
        account_prefix, flawed_figure_index, account_suffix, _, _ = flawed_account
        flawed_figure_superposition = cls.of_flawed_figures()[flawed_figure_index]
        prefix_superpositions = cls.from_account(account_prefix)
        suffix_superpositions = cls.from_account(account_suffix)
        return prefix_superpositions + [flawed_figure_superposition] + suffix_superpositions

class Results:
    "methods that provide Results for testing"

    @staticmethod
    def of_example_accounts():
        "return Results from example accounts"
        return pipe(fixture_constants.example_accounts, _third_elements, tuple)

    @staticmethod
    def of_basic_input_file():
        "return Results from the basic input file"
        return fixture_constants.BasicInputFile.results

    @staticmethod
    def of_advanced_input_file():
        "return Results from the advanced input file"
        return fixture_constants.AdvancedInputFile.results

    @staticmethod
    def of_flawed_accounts():
        "return Results of Accounts including flawed figures"
        return pipe(fixture_constants.flawed_accounts, _fifth_elements, tuple)

class ArbitraryValues:
    "methods that provide arbitrary values for testing"

    _all = (0, 1, -10, -999999999, 123456789, 3.14159, -.00000000001,
            False, True, [], (), {}, '', None, object, int, list, dict, bool,
            [1, 2, 3], {1: 2}, {0}, (1, 2, 3), {1: 'a', 2: 'b'},
            'abc', '|', '-', '\r', 'foo', '1', '0', 'c', '=', '\t', '\r',
            u'abc', u'|', u'-', u'\r', u'foo', u'1', u'0', u'c', u'=', u'\t', u'\r',
            )

    @classmethod
    def non_iterables(cls):
        "return a list of arbitrary values over which one cannot iterate"
        not_iterable = lambda value: not cls._iterable(value)
        return filter(not_iterable, cls._all)

    @staticmethod
    def _iterable(value):
        "return True if value iterable"
        try:
            iterator = iter(value)
            return True
        except TypeError:
            return False

    @classmethod
    def single_character_basestrings(cls):
        "return list of arbitrary single character basestrings"
        litmus = lambda value: len(value) == 1
        return filter(litmus, cls.basestrings())

    @classmethod
    def basestrings(cls):
        "return list of arbitrary basestrings"
        litmus = lambda value: isinstance(value, basestring)
        return filter(litmus, cls._all)

    @classmethod
    def non_basestrings(cls):
        "return set of arbitrary values that includes no basestrings"
        litmus = lambda value: not isinstance(value, basestring)
        return filter(litmus, cls._all)

    @classmethod
    def of_different_type(cls, value_or_type):
        "Return an arbitrary value not of value_or_type"
        avoided_type = cls._type(value_or_type)
        different_type = lambda value: not isinstance(value, avoided_type)
        return filter(different_type, cls._all)

    @staticmethod
    def _type(value_or_type):
        "return expected type"
        if isinstance(value_or_type, type):
            return value_or_type
        else:
            return type(value_or_type)

class Paths:
    "methods that provide Paths for testing"

    _input_files_parent_directory = os.path.dirname(fixture_constants.__file__)
    _path_to_input_files = os.path.join(_input_files_parent_directory, 'input_files')

    @classmethod
    def basic_input_file(cls):
        "return the path to the basic input file"
        directory = cls._path_to_input_files
        file_name = fixture_constants.BasicInputFile.file_name
        return os.path.join(directory, file_name)

    @classmethod
    def advanced_input_file(cls):
        "return the path to the advanced input file"
        directory = cls._path_to_input_files
        file_name = fixture_constants.AdvancedInputFile.file_name
        return os.path.join(directory, file_name)

    @classmethod
    def parse(cls):
        "return the path to the parse application"
        directory = os.path.dirname(parse.__file__)
        file_name = 'parse'
        return os.path.join(directory, file_name)
