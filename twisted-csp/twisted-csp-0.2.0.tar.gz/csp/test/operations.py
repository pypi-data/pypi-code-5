from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred

from csp.test_helpers import async
from csp import Channel, put, take, alts, go, sleep, stop
from csp import put_then_callback, take_then_callback
from csp import DEFAULT
from csp import operations as ops


class Operations(TestCase):
    @async
    def test_from_coll(self):
        nums = range(10)
        ch = ops.from_coll(nums)
        for num in nums:
            self.assertEqual(num, (yield take(ch)))
        self.assertEqual(True, ch.is_closed())

    @async
    def test_into(self):
        coll = ["a", "b", "c"]
        nums = range(10)
        ch = ops.from_coll(nums)
        self.assertEqual(coll + nums, (yield take(ops.into(coll, ch))))

    @async
    def test_onto(self):
        nums = range(10)
        ch = Channel()
        ops.onto(ch, nums)
        self.assertEqual(nums, (yield take(ops.into([], ch))))
