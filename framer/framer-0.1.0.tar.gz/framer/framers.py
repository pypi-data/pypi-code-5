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

import abc
import os
import struct
import sys

from cobs import cobs
from cobs import cobsr
import six

from framer import exc

# Need the MutableMapping class from collections for FramerState
if sys.version_info >= (3, 3):  # pragma: no cover
    from collections.abc import MutableMapping
else:  # pragma: no cover
    from collections import MutableMapping


@six.add_metaclass(abc.ABCMeta)
class Framer(object):
    """
    An abstract base class for framers.  Framers are responsible for
    transforming between streams of bytes and individual frames,
    through the ``to_frame()`` and ``to_bytes()`` methods.  These
    methods receive an instance of ``FramerState``, which will be
    initialized by a call to the ``initialize_state()`` method.
    """

    def initialize_state(self, state):
        """
        Initialize a ``FramerState`` object.  This state will be
        passed in to the ``to_frame()`` and ``to_bytes()`` methods,
        and may be used for processing partial frames or cross-frame
        information.  The default implementation does nothing.

        :param state: The state to initialize.
        """

        pass  # pragma: no cover

    @abc.abstractmethod
    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return ``bytes`` objects.
        """

        pass  # pragma: no cover

    @abc.abstractmethod
    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        pass  # pragma: no cover


class FramerState(MutableMapping):
    """
    Maintains state for framers.  This object may be used to store
    relevant data when a framer has consumed a part of a frame from
    the receive buffer.  It may also be used, if desired, for the
    send-side framer.  Data is stored as attributes; attribute names
    beginning with '_' are reserved.
    """

    def __init__(self):
        """
        Initialize a ``FramerState`` object.
        """

        self._data = {}

    def __getattr__(self, name):
        """
        Retrieve a state attribute.

        :param name: The name of the attribute to retrieve.

        :returns: The value of the state attribute.
        """

        # Get the data from the data dictionary
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

    def __getitem__(self, name):
        """
        Retrieve a state attribute by item access.

        :param name: The name of the attribute to retrieve.

        :returns: The value of the state attribute.
        """

        # Retrieve the data from the data dictionary
        return self._data[name]

    def __setattr__(self, name, value):
        """
        Set a state attribute.

        :param name: The name of the attribute to set.
        :param value: The desired value of the attribute.
        """

        # Attributes with a leading '_' are normal attributes
        if name[0] == '_':
            return super(FramerState, self).__setattr__(name, value)

        self._data[name] = value

    def __setitem__(self, name, value):
        """
        Set a state attribute by item access.

        :param name: The name of the attribute to set.
        :param value: The desired value of the attribute.
        """

        # Attributes with a leading '_' are special
        if name[0] == '_':
            raise KeyError(name)

        self._data[name] = value

    def __delattr__(self, name):
        """
        Delete a state attribute.

        :param name: The name of the attribute to delete.
        """

        # Attributes with a leading '_' are normal attributes
        if name[0] == '_':
            return super(FramerState, self).__delattr__(name)

        try:
            del self._data[name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

    def __delitem__(self, name):
        """
        Delete a state attribute by item access.

        :param name: The name of the attribute to delete.
        """

        # Attributes with a leading '_' are special
        if name[0] == '_':
            raise KeyError(name)

        del self._data[name]

    def __iter__(self):
        """
        Obtain an iterator over all declared state attributes.

        :returns: An iterator over the state attribute names.
        """

        return six.iterkeys(self._data)

    def __len__(self):
        """
        Obtain the length of the state--that is, the number of
        declared state attributes.

        :returns: The number of state attributes.
        """

        return len(self._data)


class IdentityFramer(Framer):
    """
    The identity framer passes received data straight through.  It is
    the simplest example of a framer.

    For this framer, frames are ``bytes``.
    """

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # Convert the data to bytes
        frame = six.binary_type(data)

        # Clear the buffer
        del data[:]

        # Return the frame
        return frame

    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        # Ensure the frame is in bytes
        return six.binary_type(frame)


class ChunkFramer(IdentityFramer):
    """
    The chunk framer passes a limited amount of data straight through.
    It is intended to be used for short-term streaming: initialize it
    with the amount of data to be received, push it onto the framer
    stack, then pop the stack when all of the data has been received.

    For this framer, frames are ``bytes``.
    """

    def __init__(self, chunk_len):
        """
        Initialize a ``ChunkFramer`` object.

        :param chunk_len: The amount of data to pass through.
        """

        super(ChunkFramer, self).__init__()

        self.chunk_len = chunk_len

    def initialize_state(self, state):
        """
        Initialize a ``FramerState`` object.  This state will be
        passed in to the ``to_frame()`` and ``to_bytes()`` methods,
        and may be used for processing partial frames or cross-frame
        information.  The default implementation does nothing.

        :param state: The state to initialize.
        """

        state.chunk_remaining = self.chunk_len

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # If we've read all the data, let the caller know
        if state.chunk_remaining <= 0:
            raise exc.NoFrames()

        # OK, how much data do we send on?
        data_len = min(state.chunk_remaining, len(data))

        # Extract that data from the buffer
        frame = six.binary_type(data[:data_len])
        del data[:data_len]

        # Update the state
        state.chunk_remaining -= data_len

        # Return the frame
        return frame


class LineFramer(Framer):
    """
    The line framer extracts lines as frames.  Lines are delimited by
    newlines or carriage return/newline pairs.  The line endings are
    stripped off.

    For this framer, frames are ``bytes``.
    """

    def __init__(self, carriage_return=True):
        """
        Initialize a ``LineFramer`` object.

        :param carriage_return: If ``True`` (the default), accept
                                carriage return/newline pairs as line
                                separators.  Also causes carriage
                                returns to be emitted.  If ``False``,
                                carriage returns are not stripped from
                                input and not emitted on output.
        """

        super(LineFramer, self).__init__()

        self.carriage_return = carriage_return
        self.line_end = b'\r\n' if carriage_return else b'\n'

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # Find the next newline
        data_len = data.find(b'\n')

        if data_len < 0:
            # No line to extract
            raise exc.NoFrames()

        # Track how much to exclude
        frame_len = data_len + 1

        # Are we to exclude carriage returns?
        if (self.carriage_return and data_len and
                data[data_len - 1] == ord(b'\r')):
            data_len -= 1

        # Extract the frame
        frame = six.binary_type(data[:data_len])
        del data[:frame_len]

        # Return the frame
        return frame

    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        # Ensure the frame is in bytes and append the delimiter
        return six.binary_type(frame) + self.line_end


class LengthEncodedFramer(Framer):
    """
    Many protocols encode their frames by prefixing the frame with the
    encoded frame length.  This abstract framer is the base class for
    such framers.  Most such framers can be implemented using
    ``StructFramer``, but other framers with unusual length encodings
    can be implemented by extending this framer and implementing the
    ``encode_length()`` and ``decode_length()`` methods.

    For this framer, frames are ``bytes``.
    """

    def initialize_state(self, state):
        """
        Initialize a ``FramerState`` object.  This state will be
        passed in to the ``to_frame()`` and ``to_bytes()`` methods,
        and may be used for processing partial frames or cross-frame
        information.  The default implementation does nothing.

        :param state: The state to initialize.
        """

        # Signal that a length must be decoded
        state.length = None

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # First, determine the length we're looking for
        length = state.length
        if length is None:
            # Try decoding a length from the data buffer
            length = self.decode_length(data, state)

        # Now, is there enough data?
        if len(data) < length:
            state.length = length
            raise exc.NoFrames()

        # Extract the frame
        frame = six.binary_type(data[:length])
        del data[:length]

        # Update the state
        state.length = None

        # Return the frame
        return frame

    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        # Generate the bytes from the frame
        frame = six.binary_type(frame)
        return self.encode_length(frame, state) + frame

    @abc.abstractmethod
    def encode_length(self, frame, state):
        """
        Encode the length of the specified frame into a sequence of
        bytes.  The frame will be appended to the byte sequence for
        transmission.

        :param frame: The frame to encode the length of.  Should be a
                      ``bytes`` object.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: The frame length, encoded into a sequence of bytes.
        """

        pass  # pragma: no cover

    @abc.abstractmethod
    def decode_length(self, data, state):
        """
        Extract and decode a frame length from the data buffer.  The
        consumed data should be removed from the buffer.  If the
        length data is incomplete, must raise a ``NoFrames``
        exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial encoded length, this object
                      can be used to store state information to allow
                      the remainder of the length to be read.

        :returns: The frame length, as an integer.
        """

        pass  # pragma: no cover


class StructFramer(LengthEncodedFramer):
    """
    A subclass of ``LengthEncodedFramer`` which encodes the frame
    length using a format string acceptable to the standard Python
    ``struct.Struct`` class.

    For this framer, frames are ``bytes``.
    """

    def __init__(self, fmt):
        """
        Initialize a ``StructFramer`` object.

        :param fmt: The ``struct``-compliant format string for the
                    integer length of the frame.
        """

        # Sanity-check the fmt
        fmt_chr = None
        for c in fmt:
            if c in '@=<>!x':
                # Modifiers and pads we can ignore
                continue

            if c in 'bBhHiIlLqQ':
                if fmt_chr:
                    raise ValueError("too many specifiers in format")
                fmt_chr = c
                continue

            # Invalid specifier for a length
            raise ValueError("unrecognized specifier in format")

        if not fmt_chr:
            # Must have *some* conversion!
            raise ValueError("no recognized specifier in format")

        super(StructFramer, self).__init__()

        # Save the format
        self.fmt = struct.Struct(fmt)

    def encode_length(self, frame, state):
        """
        Encode the length of the specified frame into a sequence of
        bytes.  The frame will be appended to the byte sequence for
        transmission.

        :param frame: The frame to encode the length of.  Should be a
                      ``bytes`` object.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: The frame length, encoded into a sequence of bytes.
        """

        # Pack the frame length
        return self.fmt.pack(len(frame))

    def decode_length(self, data, state):
        """
        Extract and decode a frame length from the data buffer.  The
        consumed data should be removed from the buffer.  If the
        length data is incomplete, must raise a ``NoFrames``
        exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial encoded length, this object
                      can be used to store state information to allow
                      the remainder of the length to be read.

        :returns: The frame length, as an integer.
        """

        # Do we have enough data yet?
        if len(data) < self.fmt.size:
            raise exc.NoFrames()

        # Extract the length
        length = self.fmt.unpack(six.binary_type(data[:self.fmt.size]))[0]
        del data[:self.fmt.size]

        # Return the length
        return length


class StuffingFramer(Framer):
    """
    Some protocols encode their frames using synchronization bytes--a
    sequence of bytes that signal the beginning and end of a frame,
    allowing for synchronization if a decoding error is encountered.
    However, the synchronization sequence could occur within the
    frame, so these protocols *stuff* a throw-away byte into such
    sequences to prevent them from accidentally ending a frame or
    starting another frame--and thus the name "byte stuffing."

    For this framer, frames are ``bytes``.
    """

    def __init__(self, begin=b'\xff\xff\xff\xff\xff',
                 end=b'\xff\xff\xff\xff\xfe', nop=b'\xff\xff\xff\xff\x00'):
        """
        Initialize a ``StuffingFramer`` object.

        :param begin: A sequence of bytes which, when encountered,
                      indicates the beginning of a frame.  Must be the
                      same length as ``end`` and ``nop``, and all
                      arguments must have a common prefix.
        :param end: A sequence of bytes which, when encountered,
                    indicates the end of a frame.  Must be the same
                    length as ``begin`` and ``nop``, and all arguments
                    must have a common prefix.
        :param nop: A sequence of bytes which, when encountered, is
                    thrown away.  Used to interrupt sequences internal
                    to the frame which could be mistaken for the
                    beginning or ending of the frame.  Must be the
                    same length as ``begin`` and ``end``, and all
                    arguments must have a common prefix.
        """

        super(StuffingFramer, self).__init__()

        # Make sure begin, end, and nop are binary types
        self.begin = six.binary_type(begin)
        self.end = six.binary_type(end)
        self.nop = six.binary_type(nop)

        # Determine the prefix
        self.prefix = os.path.commonprefix([self.begin, self.end, self.nop])

        # Do a little sanity-checking
        if not self.begin or not self.end or not self.nop:
            raise ValueError("no arguments may be empty")
        elif not self.prefix:
            raise ValueError("arguments have no common prefix")
        elif (len(self.begin) != len(self.end) or
                len(self.begin) != len(self.nop)):
            raise ValueError("arguments must be the same length")
        elif self.nop == self.begin or self.nop == self.end:
            raise ValueError("nop must be distinct from begin and end")
        elif self.begin == self.end:
            raise ValueError("begin and end must be distinct")

    def initialize_state(self, state):
        """
        Initialize a ``FramerState`` object.  This state will be
        passed in to the ``to_frame()`` and ``to_bytes()`` methods,
        and may be used for processing partial frames or cross-frame
        information.  The default implementation does nothing.

        :param state: The state to initialize.
        """

        # Signal that a start frame sequence has not been encountered
        # yet
        state.frame_start = False

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # Find the next packet start
        if not state.frame_start:
            # Find the begin sequence
            idx = data.find(self.begin)
            if idx < 0:
                # Couldn't find one
                raise exc.NoFrames()

            # Excise the begin sequence
            del data[:idx + len(self.begin)]

        # Now see if we can find the end sequence
        idx = data.find(self.end)
        if idx < 0:
            # We've found the start, but don't have the end yet
            state.frame_start = True
            raise exc.NoFrames()

        # Extract the frame
        frame = six.binary_type(data[:idx])
        del data[:idx + len(self.end)]

        # Update the state
        state.frame_start = False

        # Unstuff the frame and return it
        return self.prefix.join(frame.split(self.nop))

    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        # Generate and return the frame
        return (self.begin +
                self.nop.join(six.binary_type(frame).split(self.prefix)) +
                self.end)


class COBSFramer(Framer):
    """
    Some protocols encode their frames using synchronization bytes,
    like ``StuffingFramer``, but the byte stuffing protocol is
    Consistent Overhead Byte Stuffing, or COBS.  This framer
    implements framing where the end of a frame is delimited by the
    null character (which never appears in a COBS-encoded frame).

    For this framer, frames are ``bytes``.
    """

    # Values to pass for the variant parameter of __init__()
    VARIANT_COBS = cobs
    VARIANT_COBSR = cobsr

    def __init__(self, variant=VARIANT_COBS):
        """
        Initialize a ``COBSFramer`` object.

        :param variant: Select the COBS variant.  Valid values are
                        ``framer.COBSFramer.VARIANT_COBS`` (the
                        default) for standard COBS; and
                        ``framer.COBSFramer.VARIANT_COBSR`` for
                        COBS/R, an invention of the author of the
                        underlying ``cobs`` Python package.  It is
                        also possible to pass any object which has
                        ``encode()`` and ``decode()`` functions or
                        methods; each should take a single ``bytes``
                        argument and return ``bytes``, and the value
                        returned by ``encode()`` must not contain the
                        null character ("\0").
        """

        super(COBSFramer, self).__init__()

        # Select the variant we're using
        self.variant = variant

    def to_frame(self, data, state):
        """
        Extract a single frame from the data buffer.  The consumed
        data should be removed from the buffer.  If no complete frame
        can be read, must raise a ``NoFrames`` exception.

        :param data: A ``bytearray`` instance containing the data so
                     far read.
        :param state: An instance of ``FramerState``.  If the buffer
                      contains a partial frame, this object can be
                      used to store state information to allow the
                      remainder of the frame to be read.

        :returns: A frame.  The frame may be any object.  The stock
                  framers always return bytes.
        """

        # Find the next null byte
        data_len = data.find(b'\0')

        if data_len < 0:
            # No full frame yet
            raise exc.NoFrames()

        # Track how much to exclude
        frame_len = data_len + 1

        # Decode the data
        frame = six.binary_type(self.variant.decode(
            six.binary_type(data[:data_len])))
        del data[:frame_len]

        # Return the frame
        return frame

    def to_bytes(self, frame, state):
        """
        Convert a single frame into bytes that can be transmitted on
        the stream.

        :param frame: The frame to convert.  Should be the same type
                      of object returned by ``to_frame()``.
        :param state: An instance of ``FramerState``.  This object may
                      be used to track information across calls to the
                      method.

        :returns: Bytes that may be transmitted on the stream.
        """

        # Encode the frame and append the delimiter
        return six.binary_type(self.variant.encode(
            six.binary_type(frame))) + b'\0'
