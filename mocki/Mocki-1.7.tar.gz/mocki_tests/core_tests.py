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


def test_fake_instantiation_from_properties():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Fake

    fake = Fake(property='value', otherProperty='otherValue')

    # noinspection PyUnresolvedReferences
    assert_that(fake.property, is_(equal_to('value')))
    # noinspection PyUnresolvedReferences
    assert_that(fake.otherProperty, is_(equal_to('otherValue')))


def test_fake_equality():
    from hamcrest import assert_that

    from mocki.core import Fake

    fake = Fake(property='value', otherProperty='otherValue')

    assert_that(fake.__eq__(Fake(property='value', otherProperty='otherValue')))
    assert_that(not fake.__eq__(Fake(property='otherValue', otherProperty='value')))


def test_fake_inequality():
    from hamcrest import assert_that

    from mocki.core import Fake

    fake = Fake(property='value', otherProperty='otherValue')

    assert_that(fake.__ne__(Fake(property='otherValue', otherProperty='value')))
    assert_that(not fake.__ne__(Fake(property='value', otherProperty='otherValue')))


def test_fake_repr():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Fake

    fake = Fake(property='value', otherProperty='otherValue')

    assert_that(repr(fake), is_(equal_to("Fake(otherProperty='otherValue', property='value')")))


def test_get_mock_member_from_mock():
    from hamcrest import assert_that, equal_to, instance_of, is_, is_not, same_instance

    from mocki.core import Mock

    mock = Mock('theMock')

    mock_member = mock.theMember

    assert_that(mock_member, is_(instance_of(Mock)))

    assert_that(mock_member.name, is_(equal_to('theMock.theMember')))

    assert_that(mock_member.call_invocations, is_(same_instance(mock.call_invocations)))
    assert_that(mock_member.verified_indices, is_(same_instance(mock.verified_indices)))

    assert_that(mock.members, is_(equal_to({'theMember': mock_member})))

    assert_that(mock_member, is_(same_instance(mock.theMember)))
    assert_that(mock_member, is_not(same_instance(mock.theOtherMember)))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_invoke_call_from_mock_with_no_stub_installed(args, kwargs):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, CallInvocation

    mock = Mock('theMock')

    assert_that(mock(*args, **kwargs), is_(None))

    assert_that(mock.call_invocations, is_(equal_to([CallInvocation(mock, args, kwargs)])))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_invoke_call_from_mock_with_stub_installed(args, kwargs):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, CallInvocation

    mock = Mock('theMock')

    mock.stub = lambda call_invocation: call_invocation

    assert_that(mock(*args, **kwargs), is_(equal_to(CallInvocation(mock, args, kwargs))))

    assert_that(mock.call_invocations, is_(equal_to([CallInvocation(mock, args, kwargs)])))


def test_get_all_members_of_mock():
    from hamcrest import assert_that, contains_inanyorder

    from mocki.core import Mock

    mock = Mock('theMock')

    member_of_mock = Mock('theMember')
    other_member_of_mock = Mock('theOtherMember')

    mock.members = {
        'theMember': member_of_mock,
        'theOtherMember': other_member_of_mock,
    }

    member_of_member_of_mock = Mock('theMember')
    other_member_of_member_of_mock = Mock('theOtherMember')

    member_of_mock.members = {
        'theMember': member_of_member_of_mock,
        'theOtherMember': other_member_of_member_of_mock,
    }

    member_of_member_of_member_of_mock = Mock('theMember')
    other_member_of_member_of_member_of_mock = Mock('theOtherMember')

    member_of_member_of_mock.members = {
        'theMember': member_of_member_of_member_of_mock,
        'theOtherMember': other_member_of_member_of_member_of_mock,
    }

    assert_that(mock.all_members, contains_inanyorder(
        member_of_mock,
        other_member_of_mock,
        member_of_member_of_mock,
        other_member_of_member_of_mock,
        member_of_member_of_member_of_mock,
        other_member_of_member_of_member_of_mock,
    ))


def test_get_call_invocation_history_from_mock():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, CallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock, other_mock = Mock('theMock'), Mock('theOtherMock')

    mock.call_invocations = [
        CallInvocation(mock, '1stCall'),
        CallInvocation(other_mock, '2ndCall'),
        CallInvocation(mock, '3rdCall'),
        CallInvocation(other_mock, '4thCall'),
        CallInvocation(mock, '5thCall'),
        CallInvocation(other_mock, '6thCall'),
        CallInvocation(mock, '7thCall'),
        CallInvocation(other_mock, '8thCall'),
    ]

    matcher = lambda call_invocation: call_invocation.name in ['3rdCall', '4thCall', '7thCall', '8thCall']

    assert_that(mock.get_call_invocation_history(matcher), is_(equal_to(
        CallInvocationHistory([
            CallInvocation(mock, '1stCall'),
            CallInvocation(mock, '3rdCall'),
            CallInvocation(mock, '5thCall'),
            CallInvocation(mock, '7thCall'),

        ], matching_indices=[1, 3])
    )))


def test_get_in_order_call_invocation_history_from_mock():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, InOrderCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock, other_mock = Mock('theMock'), Mock('theOtherMock')

    member_of_mock = Mock('theMember')
    other_member_of_mock = Mock('theOtherMember')

    mock.members = {
        'theMember': member_of_mock,
        'theOtherMember': other_member_of_mock,
    }

    member_of_member_of_mock = Mock('theMember')

    member_of_mock.members = {
        'theMember': member_of_member_of_mock,
    }

    member_of_other_member_of_mock = Mock('theOtherMember')

    other_member_of_mock.members = {
        'theOtherMember': member_of_other_member_of_mock,
    }

    mock.call_invocations = [
        CallInvocation(mock, '1stCall'),
        CallInvocation(other_mock, '2ndCall'),
        CallInvocation(mock, '3rdCall'),
        CallInvocation(other_mock, '4thCall'),
        CallInvocation(member_of_member_of_mock, '5thCall'),
        CallInvocation(other_mock, '6thCall'),
        CallInvocation(member_of_other_member_of_mock, '7thCall'),
        CallInvocation(other_mock, '8thCall'),
    ]

    mock.verified_indices = [4, 5, 6, 7]

    matcher = lambda call_invocation: call_invocation.name in ['3rdCall', '4thCall', '7thCall', '8thCall']

    considered_mocks = [member_of_mock, other_member_of_mock]

    assert_that(mock.get_in_order_call_invocation_history(matcher, considered_mocks), is_(equal_to(
        InOrderCallInvocationHistory([
            CallInvocation(mock, '3rdCall'),
            CallInvocation(member_of_member_of_mock, '5thCall'),
            CallInvocation(member_of_other_member_of_mock, '7thCall'),

        ], matching_indices=[0, 2], verified_indices=[1, 2])
    )))


def test_get_no_more_call_invocation_history_from_mock():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, NoMoreCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock, other_mock = Mock('theMock'), Mock('theOtherMock')

    member_of_mock = Mock('theMember')
    other_member_of_mock = Mock('theOtherMember')

    mock.members = {
        'theMember': member_of_mock,
        'theOtherMember': other_member_of_mock,
    }

    mock.call_invocations = [
        CallInvocation(mock, '1stCall'),
        CallInvocation(other_mock, '2ndCall'),
        CallInvocation(member_of_mock, '3rdCall'),
        CallInvocation(other_mock, '4thCall'),
        CallInvocation(mock, '5thCall'),
        CallInvocation(other_mock, '6thCall'),
        CallInvocation(other_member_of_mock, '7thCall'),
        CallInvocation(other_mock, '8thCall'),
    ]

    mock.verified_indices = [4, 5, 6, 7]

    assert_that(mock.get_no_more_call_invocation_history(), is_(equal_to(
        NoMoreCallInvocationHistory([
            CallInvocation(mock, '1stCall'),
            CallInvocation(member_of_mock, '3rdCall'),
            CallInvocation(mock, '5thCall'),
            CallInvocation(other_member_of_mock, '7thCall'),

        ], verified_indices=[2, 3])
    )))


def test_start_stubbing_from_mock():
    from hamcrest import assert_that, equal_to, instance_of, is_, same_instance

    from mocki.core import Mock, PartialStubbing

    mock = Mock('theMock')

    partial_stubbing = mock.on('theMatcher')

    assert_that(partial_stubbing, is_(instance_of(PartialStubbing)))

    assert_that(partial_stubbing.mock, is_(same_instance(mock)))

    assert_that(partial_stubbing.matcher, is_(equal_to('theMatcher')))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_start_stubbing_from_mock_using_builtin_matcher(args, kwargs):
    from hamcrest import assert_that, equal_to, instance_of, is_, same_instance

    from mocki.core import Mock, PartialStubbing

    class BuiltinMatcherFakeType(object):
        def __init__(self, matcher):
            self.matcher = matcher

        def __call__(self, *this_args, **this_kwargs):
            return self.matcher if (this_args, this_kwargs) == (args, kwargs) else None

    mock = Mock('theMock')

    mock.builtin_matchers = {
        'BuiltinMatcher': BuiltinMatcherFakeType('theMatcher'),
        'OtherBuiltinMatcher': BuiltinMatcherFakeType('theOtherMatcher'),
    }

    partial_stubbing = mock.on_builtin_matcher(*args, **kwargs)

    assert_that(partial_stubbing, is_(instance_of(PartialStubbing)))

    assert_that(partial_stubbing.mock, is_(same_instance(mock)))

    assert_that(partial_stubbing.matcher, is_(equal_to('theMatcher')))


def test_start_verification_from_mock():
    from hamcrest import assert_that, equal_to, instance_of, is_, same_instance

    from mocki.core import Mock, PartialVerification

    mock = Mock('theMock')

    partial_verification = mock.verify('theMatcher')

    assert_that(partial_verification, is_(instance_of(PartialVerification)))

    assert_that(partial_verification.mock, is_(same_instance(mock)))

    assert_that(partial_verification.matcher, is_(equal_to('theMatcher')))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_start_verification_from_mock_using_builtin_matcher(args, kwargs):
    from hamcrest import assert_that, equal_to, instance_of, is_, same_instance

    from mocki.core import Mock, PartialVerification

    class BuiltinMatcherFakeType(object):
        def __init__(self, matcher):
            self.matcher = matcher

        def __call__(self, *this_args, **this_kwargs):
            return self.matcher if (this_args, this_kwargs) == (args, kwargs) else None

    mock = Mock('theMock')

    mock.builtin_matchers = {
        'BuiltinMatcher': BuiltinMatcherFakeType('theMatcher'),
        'OtherBuiltinMatcher': BuiltinMatcherFakeType('theOtherMatcher'),
    }

    partial_verification = mock.verify_builtin_matcher(*args, **kwargs)

    assert_that(partial_verification, is_(instance_of(PartialVerification)))

    assert_that(partial_verification.mock, is_(same_instance(mock)))

    assert_that(partial_verification.matcher, is_(equal_to('theMatcher')))


def test_finish_stubbing_from_partial_stubbing():
    from hamcrest import assert_that, equal_to, instance_of, is_

    from mocki.core import Mock, PartialStubbing, Stub

    mock = Mock('theMock')

    mock.stub = 'theInitialStub'

    partial_stubbing = PartialStubbing(mock, 'theMatcher')

    partial_stubbing.do('theAction')

    assert_that(mock.stub, is_(instance_of(Stub)))

    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.matcher, is_(equal_to('theMatcher')))
    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.action, is_(equal_to('theAction')))
    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.next_stub, is_(equal_to('theInitialStub')))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_finish_stubbing_from_partial_stubbing_using_builtin_action(args, kwargs):
    from hamcrest import assert_that, equal_to, instance_of, is_

    from mocki.core import Mock, PartialStubbing, Stub

    class BuiltinActionFakeType(object):
        def __init__(self, action):
            self.action = action

        def __call__(self, *this_args, **this_kwargs):
            return self.action if (this_args, this_kwargs) == (args, kwargs) else None

    mock = Mock('theMock')

    mock.stub = 'theInitialStub'

    partial_stubbing = PartialStubbing(mock, 'theMatcher')

    partial_stubbing.builtin_actions = {
        'BuiltinAction': BuiltinActionFakeType('theAction'),
        'OtherBuiltinAction': BuiltinActionFakeType('theOtherAction'),
    }

    partial_stubbing.do_builtin_action(*args, **kwargs)

    assert_that(mock.stub, is_(instance_of(Stub)))

    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.matcher, is_(equal_to('theMatcher')))
    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.action, is_(equal_to('theAction')))
    # noinspection PyUnresolvedReferences
    assert_that(mock.stub.next_stub, is_(equal_to('theInitialStub')))


def test_apply_stub_to_matching_call_invocation():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Stub

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    stub = Stub(
        matcher=lambda call_invocation: call_invocation == CallInvocation(name='1stCall'),
        action=lambda call_invocation: call_invocation,

        next_stub=None,
    )

    assert_that(stub(CallInvocation(name='1stCall')), is_(equal_to(CallInvocation(name='1stCall'))))


def test_apply_stub_to_non_matching_call_invocation():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Stub

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    stub = Stub(
        matcher=lambda call_invocation: call_invocation != CallInvocation(name='1stCall'),
        next_stub=lambda call_invocation: call_invocation,

        action=None,
    )

    assert_that(stub(CallInvocation(name='1stCall')), is_(equal_to(CallInvocation(name='1stCall'))))


def test_finish_verification_from_partial_verification(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import PartialVerification

    class DoVerificationFake(object):
        def __call__(self, mock, matcher, expectation):
            # noinspection PyAttributeOutsideInit
            self.mock, self.matcher, self.expectation = mock, matcher, expectation

    do_verification = DoVerificationFake()

    monkeypatch.setattr('mocki.core.do_verification', do_verification)

    partial_verification = PartialVerification('theMock', 'theMatcher')

    partial_verification.invoked('theExpectation')

    assert_that(do_verification.mock, is_(equal_to('theMock')))
    assert_that(do_verification.matcher, is_(equal_to('theMatcher')))
    assert_that(do_verification.expectation, is_(equal_to('theExpectation')))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args, kwargs', [
    ((), {}),
    (('value1', 'value2'), {}),
    ((), {'kw1': 'value1', 'kw2': 'value2'}),
    (('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'}),
])
def test_finish_verification_from_partial_verification_using_builtin_expectation(args, kwargs, monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import PartialVerification

    class DoVerificationFake(object):
        def __call__(self, mock, matcher, expectation):
            # noinspection PyAttributeOutsideInit
            self.mock, self.matcher, self.expectation = mock, matcher, expectation

    class BuiltinExpectationFakeType(object):
        def __init__(self, expectation):
            self.expectation = expectation

        def __call__(self, *this_args, **this_kwargs):
            return self.expectation if (this_args, this_kwargs) == (args, kwargs) else None

    do_verification = DoVerificationFake()

    monkeypatch.setattr('mocki.core.do_verification', do_verification)

    partial_verification = PartialVerification('theMock', 'theMatcher')

    partial_verification.builtin_expectations = {
        'BuiltinExpectation': BuiltinExpectationFakeType('theExpectation'),
        'OtherBuiltinExpectation': BuiltinExpectationFakeType('theOtherExpectation'),
    }

    partial_verification.invoked_builtin_expectation(*args, **kwargs)

    assert_that(do_verification.mock, is_(equal_to('theMock')))
    assert_that(do_verification.matcher, is_(equal_to('theMatcher')))
    assert_that(do_verification.expectation, is_(equal_to('theExpectation')))


def test_finish_in_order_verification_from_partial_verification(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import PartialVerification

    class DoInOrderVerificationFake(object):
        def __call__(self, mock, matcher, considered_mocks):
            # noinspection PyAttributeOutsideInit
            self.mock, self.matcher, self.considered_mocks = mock, matcher, considered_mocks

    do_in_order_verification = DoInOrderVerificationFake()

    monkeypatch.setattr('mocki.core.do_in_order_verification', do_in_order_verification)

    partial_verification = PartialVerification('theMock', 'theMatcher')

    partial_verification.invoked_in_order('theConsideredMock', 'theOtherConsideredMock')

    assert_that(do_in_order_verification.mock, is_(equal_to('theMock')))
    assert_that(do_in_order_verification.matcher, is_(equal_to('theMatcher')))
    assert_that(do_in_order_verification.considered_mocks, contains('theConsideredMock', 'theOtherConsideredMock'))


def test_do_verification():
    from hamcrest import assert_that, contains

    from mocki.core import Mock, do_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    expectation = lambda call_invocations: call_invocations == [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    do_verification(mock, matcher, expectation)

    assert_that(mock.verified_indices, contains(1, 3))


def test_do_verification_failing_with_no_call_invoked():
    from hamcrest import assert_that, equal_to, contains, is_

    from mocki.core import Mock, do_verification

    mock = Mock('theMock')

    mock.call_invocations = []

    matcher = lambda call_invocation: call_invocation in []

    expectation = lambda call_invocations: call_invocations != []

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_verification(mock, matcher, expectation))

    assert_that(str(excinfo.value), is_(equal_to('No call invoked from theMock.')))

    assert_that(mock.verified_indices, contains())


def test_do_verification_failing_with_no_matching_call_invoked(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    matcher = lambda call_invocation: call_invocation in []

    expectation = lambda call_invocations: call_invocations != []

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_verification(mock, matcher, expectation))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found no matching call invoked from theMock :',

        '  1stCall',
        '  2ndCall',
        '  3rdCall',
        '  4thCall',
    ]))))

    assert_that(mock.verified_indices, contains())


def test_do_verification_failing_with_one_matching_call_invoked(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
    ]

    expectation = lambda call_invocations: call_invocations != [
        CallInvocation(mock, name='2ndCall'),
    ]

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_verification(mock, matcher, expectation))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found one matching call invoked from theMock :',

        '  1stCall',
        '> 2ndCall',
        '  3rdCall',
        '  4thCall',
    ]))))

    assert_that(mock.verified_indices, contains())


def test_do_verification_failing_with_several_matching_calls_invoked(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    expectation = lambda call_invocations: call_invocations != [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_verification(mock, matcher, expectation))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found 2 matching calls invoked from theMock :',

        '  1stCall',
        '> 2ndCall',
        '  3rdCall',
        '> 4thCall',
    ]))))

    assert_that(mock.verified_indices, contains())


def test_do_in_order_verification_with_no_verified_index():
    from hamcrest import assert_that, contains

    from mocki.core import Mock, do_in_order_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='5thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    mock.verified_indices = []

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    do_in_order_verification(mock, matcher, considered_mocks=[mock])

    assert_that(mock.verified_indices, contains(1))


def test_do_in_order_verification_with_verified_indices():
    from hamcrest import assert_that, contains

    from mocki.core import Mock, do_in_order_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='5thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    mock.verified_indices = [0, 1]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    do_in_order_verification(mock, matcher, considered_mocks=[mock])

    assert_that(mock.verified_indices, contains(0, 1, 3))


def test_do_in_order_verification_failing_with_no_call_invoked():
    from hamcrest import assert_that, equal_to, contains, is_

    from mocki.core import Mock, do_in_order_verification

    mock = Mock('theMock')

    mock.call_invocations = []

    mock.verified_indices = []

    matcher = lambda call_invocation: call_invocation in []

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_in_order_verification(mock, matcher, considered_mocks=[mock]))

    assert_that(str(excinfo.value), is_(equal_to('No call invoked from theMock.')))

    assert_that(mock.verified_indices, contains())


def test_do_in_order_verification_failing_with_no_matching_call_invoked(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_in_order_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='5thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    mock.verified_indices = [4, 5]

    matcher = lambda call_invocation: call_invocation in []

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_in_order_verification(mock, matcher, considered_mocks=[mock]))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found no matching call invoked from theMock :',

        '    1stCall',
        '    2ndCall',
        '    3rdCall',
        '    4thCall',
        'X   5thCall',
        'X   6thCall',
    ]))))

    assert_that(mock.verified_indices, contains(4, 5))


def test_do_in_order_verification_failing_with_one_matching_call_invoked_but_not_in_order(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_in_order_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='5thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    mock.verified_indices = [4, 5]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
    ]

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_in_order_verification(mock, matcher, considered_mocks=[mock]))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found one matching call invoked from theMock, but not in order :',

        '    1stCall',
        '  > 2ndCall',
        '    3rdCall',
        '    4thCall',
        'X   5thCall',
        'X   6thCall',
    ]))))

    assert_that(mock.verified_indices, contains(4, 5))


def test_do_in_order_verification_failing_with_several_matching_calls_invoked_but_not_in_order(monkeypatch):
    from hamcrest import assert_that, contains, equal_to, is_

    from mocki.core import Mock, do_in_order_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
        CallInvocation(mock, name='4thCall'),
        CallInvocation(mock, name='5thCall'),
        CallInvocation(mock, name='6thCall'),
    ]

    mock.verified_indices = [4, 5]

    matcher = lambda call_invocation: call_invocation in [
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='4thCall'),
    ]

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_in_order_verification(mock, matcher, considered_mocks=[mock]))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found 2 matching calls invoked from theMock, but not in order :',

        '    1stCall',
        '  > 2ndCall',
        '    3rdCall',
        '  > 4thCall',
        'X   5thCall',
        'X   6thCall',
    ]))))

    assert_that(mock.verified_indices, contains(4, 5))


def test_do_no_more_verification():
    from mocki.core import Mock, do_no_more_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
    ]

    mock.verified_indices = [0, 1, 2]

    do_no_more_verification(mock)


def test_do_no_more_verification_failing_with_one_non_verified_call_invoked(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, do_no_more_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
    ]

    mock.verified_indices = [0, 2]

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_no_more_verification(mock))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found one call invoked from theMock that was not verified :',

        'X 1stCall',
        '  2ndCall',
        'X 3rdCall',
    ]))))


def test_do_no_more_verification_failing_with_several_non_verified_call_invoked(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, do_no_more_verification

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock name')

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    mock = Mock('theMock')

    mock.call_invocations = [
        CallInvocation(mock, name='1stCall'),
        CallInvocation(mock, name='2ndCall'),
        CallInvocation(mock, name='3rdCall'),
    ]

    mock.verified_indices = []

    # noinspection PyUnresolvedReferences
    excinfo = pytest.raises(AssertionError, lambda: do_no_more_verification(mock))

    assert_that(str(excinfo.value), is_(equal_to('\n'.join([
        'Found 3 calls invoked from theMock that was not verified :',

        '  1stCall',
        '  2ndCall',
        '  3rdCall',
    ]))))


def test_call_invocation_history_with_no_matching_index():
    from hamcrest import assert_that, contains

    from mocki.core import CallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = CallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], matching_indices=())

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains())
    assert_that(call_invocation_history.matching_call_invocations, contains())


def test_call_invocation_history_with_matching_indices():
    from hamcrest import assert_that, contains

    from mocki.core import CallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = CallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], matching_indices=[1, 3])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains(1, 3))
    assert_that(call_invocation_history.matching_call_invocations, contains(
        CallInvocation(name='2ndCall'),
        CallInvocation(name='4thCall'),
    ))


def test_print_call_invocation_history(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import print_call_invocation_history

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    # noinspection PyPep8Naming
    CallInvocationHistory = collections.namedtuple(
        'CallInvocationHistory', 'call_invocations matching_indices'
    )

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    call_invocation_history = CallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], matching_indices=[1, 3])

    assert_that(print_call_invocation_history(call_invocation_history), is_(equal_to('\n'.join([
        '  1stCall',
        '> 2ndCall',
        '  3rdCall',
        '> 4thCall',
    ]))))


def test_in_order_call_invocation_history_with_no_matching_index_or_verified_index():
    from hamcrest import assert_that, contains

    from mocki.core import InOrderCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = InOrderCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], matching_indices=[], verified_indices=[])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains())
    assert_that(call_invocation_history.matching_call_invocations, contains())

    assert_that(call_invocation_history.verified_indices, contains())
    assert_that(call_invocation_history.verified_call_invocations, contains())

    assert_that(call_invocation_history.in_order_matching_indices, contains())
    assert_that(call_invocation_history.in_order_matching_call_invocations, contains())


def test_in_order_call_invocation_history_with_matching_indices_but_no_verified_index():
    from hamcrest import assert_that, contains

    from mocki.core import InOrderCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = InOrderCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),

    ], matching_indices=[1, 3, 5, 7], verified_indices=[])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains(1, 3, 5, 7))
    assert_that(call_invocation_history.matching_call_invocations, contains(
        CallInvocation(name='2ndCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='8thCall'),
    ))

    assert_that(call_invocation_history.verified_indices, contains())
    assert_that(call_invocation_history.verified_call_invocations, contains())

    assert_that(call_invocation_history.in_order_matching_indices, contains(1, 3, 5, 7))
    assert_that(call_invocation_history.in_order_matching_call_invocations, contains(
        CallInvocation(name='2ndCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='8thCall'),
    ))


def test_in_order_call_invocation_history_with_verified_indices_but_no_matching_index():
    from hamcrest import assert_that, contains

    from mocki.core import InOrderCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = InOrderCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),

    ], matching_indices=[], verified_indices=[2, 3])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains())
    assert_that(call_invocation_history.matching_call_invocations, contains())

    assert_that(call_invocation_history.verified_indices, contains(2, 3))
    assert_that(call_invocation_history.verified_call_invocations, contains(
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.in_order_matching_indices, contains())
    assert_that(call_invocation_history.in_order_matching_call_invocations, contains())


def test_in_order_call_invocation_history_with_matching_indices_and_verified_indices():
    from hamcrest import assert_that, contains

    from mocki.core import InOrderCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = InOrderCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),

    ], matching_indices=[1, 3, 5, 7], verified_indices=[2, 3])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='5thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='7thCall'),
        CallInvocation(name='8thCall'),
    ))

    assert_that(call_invocation_history.matching_indices, contains(1, 3, 5, 7))
    assert_that(call_invocation_history.matching_call_invocations, contains(
        CallInvocation(name='2ndCall'),
        CallInvocation(name='4thCall'),
        CallInvocation(name='6thCall'),
        CallInvocation(name='8thCall'),
    ))

    assert_that(call_invocation_history.verified_indices, contains(2, 3))
    assert_that(call_invocation_history.verified_call_invocations, contains(
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.in_order_matching_indices, contains(5, 7))
    assert_that(call_invocation_history.in_order_matching_call_invocations, contains(
        CallInvocation(name='6thCall'),
        CallInvocation(name='8thCall'),
    ))


def test_print_in_order_call_invocation_history(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import print_in_order_call_invocation_history

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    # noinspection PyPep8Naming
    InOrderCallInvocationHistory = collections.namedtuple(
        'InOrderCallInvocationHistory', 'call_invocations matching_indices verified_indices'
    )

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    call_invocation_history = InOrderCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], matching_indices=[1, 3], verified_indices=[2, 3])

    assert_that(print_in_order_call_invocation_history(call_invocation_history), is_(equal_to('\n'.join([
        '    1stCall',
        '  > 2ndCall',
        'X   3rdCall',
        'X > 4thCall',
    ]))))


def test_no_more_call_invocation_history_with_no_verified_index():
    from hamcrest import assert_that, contains

    from mocki.core import NoMoreCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = NoMoreCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], verified_indices=[])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.verified_indices, contains())
    assert_that(call_invocation_history.verified_call_invocations, contains())

    assert_that((call_invocation_history.non_verified_indices, contains(0, 1, 2, 3)))
    assert_that((call_invocation_history.non_verified_call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    )))


def test_no_more_call_invocation_history_with_verified_indices():
    from hamcrest import assert_that, contains

    from mocki.core import NoMoreCallInvocationHistory

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    call_invocation_history = NoMoreCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], verified_indices=[2, 3])

    assert_that(call_invocation_history.call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.verified_indices, contains(2, 3))
    assert_that(call_invocation_history.verified_call_invocations, contains(
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),
    ))

    assert_that(call_invocation_history.non_verified_indices, contains(0, 1))
    assert_that(call_invocation_history.non_verified_call_invocations, contains(
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
    ))


def test_print_no_more_call_invocation_history(monkeypatch):
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import print_no_more_call_invocation_history

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'name')

    # noinspection PyPep8Naming
    NoMoreCallInvocationHistory = collections.namedtuple(
        'NoMoreCallInvocationHistory', 'call_invocations verified_indices'
    )

    monkeypatch.setattr('mocki.core.print_call_invocation', lambda call_invocation: call_invocation.name)

    call_invocation_history = NoMoreCallInvocationHistory([
        CallInvocation(name='1stCall'),
        CallInvocation(name='2ndCall'),
        CallInvocation(name='3rdCall'),
        CallInvocation(name='4thCall'),

    ], verified_indices=[2, 3])

    assert_that(print_no_more_call_invocation_history(call_invocation_history), is_(equal_to('\n'.join([
        '  1stCall',
        '  2ndCall',
        'X 3rdCall',
        'X 4thCall',
    ]))))


def test_print_call_invocation_with_no_arg_or_kwarg():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, print_call_invocation

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock args kwargs')

    call_invocation = CallInvocation(Mock('theMock'), (), {})

    assert_that(print_call_invocation(call_invocation), is_(equal_to(
        'theMock()'
    )))


def test_print_call_invocation_with_args_but_no_kwarg():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, print_call_invocation

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock args kwargs')

    call_invocation = CallInvocation(Mock('theMock'), ('value1', 'value2'), {})

    assert_that(print_call_invocation(call_invocation), is_(equal_to(
        "theMock('value1', 'value2')"
    )))


def test_print_call_invocation_with_kwargs_but_no_arg():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, print_call_invocation

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock args kwargs')

    call_invocation = CallInvocation(Mock('theMock'), (), {'kw1': 'value1', 'kw2': 'value2'})

    assert_that(print_call_invocation(call_invocation), is_(equal_to(
        "theMock(kw1='value1', kw2='value2')"
    )))


def test_print_call_invocation_with_args_and_kwargs():
    from hamcrest import assert_that, equal_to, is_

    from mocki.core import Mock, print_call_invocation

    # noinspection PyPep8Naming
    CallInvocation = collections.namedtuple('CallInvocation', 'mock args kwargs')

    call_invocation = CallInvocation(Mock('theMock'), ('value1', 'value2'), {'kw1': 'value1', 'kw2': 'value2'})

    assert_that(print_call_invocation(call_invocation), is_(equal_to(
        "theMock('value1', 'value2', kw1='value1', kw2='value2')"
    )))
