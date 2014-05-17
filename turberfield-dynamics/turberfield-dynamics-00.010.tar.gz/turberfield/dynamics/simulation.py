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
from asyncio.queues import QueueEmpty
from collections import deque
from collections.abc import MutableSequence
from functools import singledispatch
import itertools
import unittest
import warnings

from turberfield.dynamics.jobqueue import JobQueue
from turberfield.dynamics.types import Stop
from turberfield.dynamics.types import Tick


__doc__ = """
Here's how you would set up and run a simulation:

.. code-block:: python

    # The asyncio module is standard in Python 3.4 and above
    loop = asyncio.get_event_loop()

    # Create a generator for the simulation 'tick-stream'
    ticks = Simulation.ticks(0, 10, 1)

    # More about the JobQueue later...
    jq = JobQueue(loop=loop)

    # Simulation will run only a single task; 'agent', defined below.
    tasks = [Simulation.task(loop, agent, jq)]

    # Initialise the simulation object
    sim = Simulation(tasks, jq)

    # Run the simulation until it finishes or times out.
    loop.run_until_complete(asyncio.wait_for(
        sim.dispatch(ticks), loop=loop, timeout=1))


What is a task? It's a function or method which listens for the passage of
time and which can ask for things to happen in the future.
Here's what the task ``agent`` might look like:

.. code-block:: python

    @asyncio.coroutine
    def agent(q, jq, priority):
        tick = None
        while type(tick) is not Stop:
            tick = yield from q.get()
            # Do stuff...
            msg = "For the attention of..."
            yield from jq.put(tick.t + 1, priority, msg)
        else:
            return tick

``Agent`` is a coroutine. To work with the Turberfield simulator, it must
have these three positional parameters; `q`, `jq`, and `priority`:

    q
        Your task gets its :py:class:`ticks <turberfield.dynamics.types.Tick>`
        from this object.
    jq
        This is a :py:class:`~turberfield.dynamics.jobqueue.JobQueue` which
        your task uses to post messages.

    priority
        This is assigned to your task by the Turberfield simulator as
        a unique integer, thereby eliminating contention with other coroutines.

"""


@singledispatch
def message_handler(msg, *args, **kwargs):
    """
    The simulation calls this function, passing to it every message
    which pops up in the job queue.

    This function has been wrapped with the ``functools.singledispatch``
    decorator.

    So, to register your own supplied function as a handler for a particular
    class of message, make a call like the following::

        message_handler.register(type(msg), custom_handler)

    """
    warnings.warn("No handler found for {}".format(msg))
    rv = asyncio.Future()
    rv.set_result(msg)
    return rv


class Simulation:
    """
    The simulator in Turberfield is a shareable object. You need to
    define it once in your main module::

        sim = Simulation(tasks, jq, buf)

    Elsewhere, you can grab a readable copy like this::

        sim = Simulation(None)

    tasks
        A list of task objects. Each should be the result of a call
        to :py:func:`Simulation.task\
<turberfield.dynamics.simulation.Simulation.task>`.
    jq (optional)
        A :py:class:`~turberfield.dynamics.jobqueue.JobQueue` object.
        The simulation will get its messages here.
    buf (optional)
        A container which will record jobs as they are processed by the
        simulation. This can be useful for debugging purposes. If you
        omit this argument, the Simulation object will create its own
        (small) buffer.

    """

    _shared_state = {}

    @staticmethod
    def task(loop, fn, jq, priority=1, *args, **kwargs):
        """
        Create a `asyncio.Task` for `fn` (which must be a coroutine).
        The returned object is decorated with attributes necessary for
        use with a :py:class:`~turberfield.dynamics.simulation.Simulation`
        object. `jq` should be a
        :py:class:`~turberfield.dynamics.jobqueue.JobQueue` object common
        to all the tasks in your simulation.

        """
        q = asyncio.Queue(loop=loop)
        coro = fn(q, jq, priority, *args, **kwargs)
        rv = asyncio.Task(coro, loop=loop)
        rv.q = q
        rv.priority = priority
        return rv

    @staticmethod
    def ticks(start, end, interval):
        """
        Returns a generator of
        :py:class:`Ticks <turberfield.dynamics.types.Tick>` which will
        end with a
        :py:class:`Stop <turberfield.dynamics.types.Stop>`.

        """
        return itertools.chain(
            (Tick(i, 0) for i in range(start, end, interval)),
            [Stop(end, 0)])

    def __init__(self, tasks, jq=None, buf=None):
        self.__dict__ = self._shared_state
        if jq and not hasattr(self, "buf"):
            self.jq = jq
            self.buf = buf if isinstance(buf, deque) else deque(maxlen=32)
        if isinstance(tasks, list):
            if not hasattr(self, "jq"):
                warnings.warn("Simulation lacks a job queue")
            self.tasks = tasks

    def _clear(self):
        del self.jq
        del self.tasks
        del self.buf

    @asyncio.coroutine
    def dispatch(self, ticks):
        """
        The coroutine which drives the simulation loop.

        ticks
            An iterable of
            :py:class:`Ticks <turberfield.dynamics.types.Tick>` which
            ends with a
            :py:class:`Stop <turberfield.dynamics.types.Stop>`.

        """
        for tick in ticks:
            yield from asyncio.sleep(0)
            for tsk in (i for i in self.tasks if not i.done()):
                try:
                    yield from tsk.q.put(tick)
                except AttributeError as e:
                    warnings.warning("Task {} has no queue".format(tsk))
                    continue

            while True:
                try:
                    job, msg = self.jq.get_nowait()
                except QueueEmpty:
                    break
                else:
                    if tick.t < job.t:
                        yield from self.jq.put(job.t, job.priority, msg)
                        break
                    else:
                        self.buf.append((job, msg))
                        rv = yield from message_handler(
                            msg, Tick(tick.t, job.priority), self.jq)
        else:
            return tick
