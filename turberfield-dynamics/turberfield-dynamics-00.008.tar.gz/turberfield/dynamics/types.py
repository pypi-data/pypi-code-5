#!/usr/bin/env python3.4
#   encoding: UTF-8

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

from collections import namedtuple

Tick = namedtuple("Tick", ["t", "priority"])
Tick.__doc__ = """A named tuple of {} to specify the time and priority order
of a message.""".format(Tick._fields)

Stop = namedtuple("Stop", ["t", "priority"])
Stop.__doc__ = """A special case of
:py:class:`~turberfield.dynamics.types.Tick`
which terminates a time sequence.""".format(Stop._fields)
