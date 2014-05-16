#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
#   version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License along with Mocki. If not, see
#   <http://www.gnu.org/licenses/>.
#

import collections
import pytest


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, False), (1, True), (2, True),
])
def test_apply_at_least_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import AtLeast

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = AtLeast(1)

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, False), (1, True), (2, True),
])
def test_apply_at_least_once_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import AtLeastOnce

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = AtLeastOnce()

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, True), (1, True), (2, False),
])
def test_apply_at_most_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import AtMost

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = AtMost(1)

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, True), (1, True), (2, False),
])
def test_apply_at_most_once_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import AtMostOnce

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = AtMostOnce()

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, False), (1, True), (2, True), (3, True), (4, False),
])
def test_apply_between_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import Between

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = Between(1, 3)

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, False), (1, True), (2, False),
])
def test_apply_exactly_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import Exactly

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = Exactly(1)

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, True), (1, False),
])
def test_apply_never_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import Never

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = Never()

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('nb_call_invocations, result', [
    (0, False), (1, True), (2, False),
])
def test_apply_once_expectation(nb_call_invocations, result):
    from hamcrest import assert_that, is_

    from mocki.expectations import Once

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    expectation = Once()

    call_invocations = [CallInvocation() for _ in range(nb_call_invocations)]

    assert_that(expectation(call_invocations), is_(result))
