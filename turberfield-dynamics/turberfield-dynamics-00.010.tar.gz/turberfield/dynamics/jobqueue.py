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
from collections import namedtuple


class JobQueue:
    """
    You create a JobQueue just as you would a standard Queue from the
    `asyncio` module.
    """

    Job = namedtuple("Job", ["t", "priority", "id"])

    def __init__(self, loop):
        self.loop = loop
        self.queue = asyncio.PriorityQueue(loop=loop)
        self.jobs = {}

    def get(self):
        """
        Returns a 2-tuple from the queue, consisting of:

        job
            A :py:class:`~turberfield.dynamics.JobQueue.Job` object,
            consisting of `(t, priority, id)`.
        msg
            The message delivered by the job.

        """
        job = yield from self.queue.get()
        return (job, self.jobs.pop(job.id))

    def get_nowait(self):
        job = self.queue.get_nowait()
        return (job, self.jobs.pop(job.id))

    def put(self, t, priority, msg):
        """
        Place a message on the queue, to be processed at time `t` with priority
        `priority`.

        """
        self.jobs[id(msg)] = msg
        yield from self.queue.put(JobQueue.Job(t, priority, id(msg)))

    def put_nowait(self, t, priority, msg):
        self.jobs[id(msg)] = msg
        self.queue.put_nowait(JobQueue.Job(t, priority, id(msg)))
