#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from collections import deque
import unittest
import warnings

from turberfield.dynamics.simulation import JobQueue
from turberfield.dynamics.simulation import Simulation
from turberfield.dynamics.simulation import Stop
from turberfield.dynamics.simulation import Tick


class FreshLoop(unittest.TestCase):

    def setUp(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.buf = deque()

    def tearDown(self):
        loop = asyncio.get_event_loop()
        loop.stop()
        loop.close()

    @asyncio.coroutine
    def loopback(self, q, jq, priority):
        tick = None
        self.nItems = 0
        while type(tick) is not Stop:
            tick = yield from q.get()
            yield from jq.put(tick.t, priority, tick)
            self.nItems += 1
        else:
            return tick


class TestTicks(unittest.TestCase):

    def test_ticks_fill_interval(self):
        seq = list(Simulation.ticks(0, 60, 1))
        self.assertEqual(59, max(i.t for i in seq if isinstance(i, Tick)))

    def test_ticks_non_repeating(self):
        seq = list(Simulation.ticks(0, 60, 1))
        self.assertEqual(len(set(seq)), len(seq))

    def test_ticks_end_with_stop(self):
        seq = list(Simulation.ticks(0, 60, 1))
        self.assertTrue(isinstance(seq[-1], Stop))
        self.assertEqual(60, seq[-1].t)


class TestTasks(FreshLoop):

    def test_task_has_queue(self):
        loop = asyncio.get_event_loop()
        jq = JobQueue(loop=loop)
        tsk = Simulation.task(loop, self.loopback, jq)
        self.assertTrue(hasattr(tsk, "q"))


class TestSimulation(FreshLoop):

    def test_ticks(self):
        loop = asyncio.get_event_loop()
        ticks = Simulation.ticks(0, 6, 1)
        jq = JobQueue(loop=loop)
        tsk = Simulation.task(loop, self.loopback, jq)
        sim = Simulation([tsk], jq, self.buf)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            try:
                loop.run_until_complete(asyncio.wait_for(
                    sim.dispatch(ticks), loop=loop, timeout=1))
                self.assertEqual(7, self.nItems)
                self.assertEqual(6, len(self.buf))
            except TimeoutError as e:
                self.fail(e)
            finally:
                sim._clear()
                self.assertFalse(hasattr(sim, "buf"))
                self.assertFalse(hasattr(sim, "jq"))
                self.assertFalse(hasattr(sim, "tasks"))
