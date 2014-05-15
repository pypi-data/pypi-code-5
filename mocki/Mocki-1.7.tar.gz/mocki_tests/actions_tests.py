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


def test_execute_return_action():
    from hamcrest import assert_that, equal_to, is_

    from mocki.actions import Return

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    action = Return('value')

    assert_that(action(CallInvocation()), is_(equal_to('value')))


def test_execute_raise_action():
    from hamcrest import assert_that, equal_to, is_

    from mocki.actions import Raise

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', '')

    action = Raise(Exception('theException'))

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(Exception, lambda: action(CallInvocation()))

    assert_that(str(excinfo.value), is_(equal_to('theException')))


def test_execute_one_action_in_order():
    from hamcrest import assert_that, equal_to, is_

    from mocki.actions import InOrder

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    action = InOrder(
        lambda call_invocation: '1stAction-%s' % call_invocation.name,
    )

    assert_that(action(CallInvocation(name='1stCall')), is_(equal_to('1stAction-1stCall')))
    assert_that(action(CallInvocation(name='2ndCall')), is_(equal_to('1stAction-2ndCall')))


def test_execute_several_actions_in_order():
    from hamcrest import assert_that, equal_to, is_

    from mocki.actions import InOrder

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    action = InOrder(
        lambda call_invocation: '1stAction-%s' % call_invocation.name,
        lambda call_invocation: '2ndAction-%s' % call_invocation.name,
        lambda call_invocation: '3rdAction-%s' % call_invocation.name,
    )

    assert_that(action(CallInvocation(name='1stCall')), is_(equal_to('1stAction-1stCall')))
    assert_that(action(CallInvocation(name='2ndCall')), is_(equal_to('2ndAction-2ndCall')))
    assert_that(action(CallInvocation(name='3rdCall')), is_(equal_to('3rdAction-3rdCall')))
    assert_that(action(CallInvocation(name='4thCall')), is_(equal_to('3rdAction-4thCall')))
