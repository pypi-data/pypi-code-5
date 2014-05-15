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


def test_apply_any_call_matcher():
    from hamcrest import assert_that, is_

    from mocki.matchers import AnyCall

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    matcher = AnyCall()

    assert_that(matcher(CallInvocation()), is_(True))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs, result', [
    ((), {}, True),
    (('value1', 'value2'), {}, False),
    ((), {'kw1': 'value1', 'kw2': 'value2'}, False),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}, False),
])
def test_apply_call_matcher_with_no_arg_or_kwarg(args, kwargs, result):
    from hamcrest import assert_that, is_

    from mocki.matchers import Call

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'args kwargs')

    matcher = Call()

    assert_that(matcher(CallInvocation(args, kwargs)), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs, result', [
    ((), {}, False),
    (('value1', 'value2'), {}, True),
    (('otherValue1', 'otherValue2'), {}, False),
    ((), {'kw1': 'value1', 'kw2': 'value2'}, False),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}, False),
])
def test_apply_call_matcher_with_args_but_no_kwarg(args, kwargs, result):
    from hamcrest import assert_that, is_

    from mocki.matchers import Call

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'args kwargs')

    matcher = Call('value1', 'value2')

    assert_that(matcher(CallInvocation(args, kwargs)), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs, result', [
    ((), {}, False),
    (('value1', 'value2'), {}, False),
    ((), {'kw1': 'value1', 'kw2': 'value2'}, True),
    ((), {'kw1': 'otherValue1', 'kw2': 'otherValue2'}, False),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}, False),
])
def test_apply_call_matcher_with_kwargs_but_no_arg(args, kwargs, result):
    from hamcrest import assert_that, is_

    from mocki.matchers import Call

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'args kwargs')

    matcher = Call(kw1='value1', kw2='value2')

    assert_that(matcher(CallInvocation(args, kwargs)), is_(result))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs, result', [
    ((), {}, False),
    (('value1', 'value2'), {}, False),
    ((), {'kw1': 'value1', 'kw2': 'value2'}, False),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}, True),
    (('otherValue1', 'otherValue2'), {'kw1': 'value1', 'kw2': 'value2'}, False),
    (('value1', 'value2'), {'kw1': 'otherValue1', 'kw2': 'otherValue2'}, False),
    (('otherValue1', 'otherValue2'), {'kw1': 'otherValue1', 'kw2': 'otherValue2'}, False),
])
def test_apply_call_matcher_with_args_and_kwargs(args, kwargs, result):
    from hamcrest import assert_that, is_

    from mocki.matchers import Call

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'args kwargs')

    matcher = Call('value1', 'value2', kw1='value1', kw2='value2')

    assert_that(matcher(CallInvocation(args, kwargs)), is_(result))


def test_arg_placeholder_from_value():
    from hamcrest import assert_that, equal_to, is_, is_not

    from mocki.matchers import ArgPlaceholder

    arg_placeholder = ArgPlaceholder('value')

    assert_that(arg_placeholder, is_(equal_to('value')))
    assert_that(arg_placeholder, is_not(equal_to('otherValue')))


def test_arg_placeholder_from_callable():
    from hamcrest import assert_that, equal_to, is_, is_not

    from mocki.matchers import ArgPlaceholder

    class EqualToCallable(object):
        def __init__(self, expected_value):
            self.expected_value = expected_value

        def __call__(self, value):
            return value == self.expected_value

    arg_placeholder = ArgPlaceholder(EqualToCallable('value'))

    assert_that(arg_placeholder, is_(equal_to('value')))
    assert_that(arg_placeholder, is_not(equal_to('otherValue')))


def test_arg_placeholder_from_arg_matcher():
    from hamcrest import assert_that, equal_to, is_, is_not

    from mocki.matchers import ArgPlaceholder

    class EqualToArgMatcher(object):
        def __init__(self, expected_value):
            self.expected_value = expected_value

        def matches(self, value):
            return value == self.expected_value

    arg_placeholder = ArgPlaceholder(EqualToArgMatcher('value'))

    assert_that(arg_placeholder, is_(equal_to('value')))
    assert_that(arg_placeholder, is_not(equal_to('otherValue')))
