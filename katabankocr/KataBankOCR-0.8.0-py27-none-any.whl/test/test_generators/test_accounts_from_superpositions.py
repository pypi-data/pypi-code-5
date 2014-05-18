"test the accounts_from_superpositions generator"

import pytest

from toolz import pipe, concat

from parse.generators.accounts_from_superpositions import accounts_from_superpositions

import check_generator
from fixture_methods import Accounts, Superpositions

test_iterability = check_generator.raises_on_non_iterable(generator=accounts_from_superpositions)

test_element_type = \
    check_generator.raises_on_bad_element_type(generator=accounts_from_superpositions,
                                               value_or_type=dict)

accounts = (Accounts.of_example_accounts(), Accounts.of_flawed_accounts())
superpositions = (Superpositions.of_example_accounts(), Superpositions.of_flawed_accounts())

def test_known_superpositions_yield_expected_account():
    "confirm known superpositions yield expected accounts"
    expected_accounts = pipe(accounts, concat, tuple)
    found_accounts = pipe(superpositions, concat, concat, accounts_from_superpositions, tuple)
    assert expected_accounts == found_accounts
