# Copyright (C) 2014 by Kevin L. Mitchell <klmitch@mit.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

import asyncio


class FramedProtocol(asyncio.BaseProtocol):
    """
    An interface for protocols expecting to receive framed data.  This
    class should be implemented almost identically to the
    ``asyncio.Protocol`` class, with the substitution of a
    ``frame_received()`` method for the ``data_received()`` method.
    """

    def frame_received(self, frame):
        """
        Called when a frame is received.

        :param frame: The frame that was received.
        """

        pass  # pragma: no cover

    def eof_received(self):
        """
        Called when the other end of the connection calls
        ``write_eof()`` or its equivalent.

        :returns: A ``False`` value (including ``None``, the default
                  return value) to cause the transport to close
                  itself, and ``True`` to leave the connection
                  half-open.
        """

        pass  # pragma: no cover
