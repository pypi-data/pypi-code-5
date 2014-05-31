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

import collections

import six

from framer import exc
from framer import framers


FramerElement = collections.namedtuple(
    'FramerElement', ('send', 'recv', 'send_state', 'recv_state'))


class FramerAdaptor(object):
    """
    The Framer transport adaptor class.  Instances of this
    class--initialized with an appropriate ``FramedProtocol``
    subclass, as well as send and receive framers--should be returned
    by the factory passed to the ``create_connection()`` or
    ``create_server()`` loop methods.
    """

    # Handlers for obtaining extra data from this transport using
    # get_extra_info()
    _handlers = {
        'send_framer': lambda p: p._send_framer,
        'send_state': lambda p: p._send_state,
        'recv_framer': lambda p: p._recv_framer,
        'recv_state': lambda p: p._recv_state,
        'recv_buf': lambda p: six.binary_type(p._recv_buf),
        'recv_paused': lambda p: p._recv_paused,
        'client_protocol': lambda p: p._client,
        'transport': lambda p: p._transport,
    }

    @classmethod
    def factory(cls, client, *args, **kwargs):
        """
        Generates and returns a callable suitable for passing as the
        ``protocol_factory`` parameter of the ``create_connection()``
        or ``create_server()`` loop methods.  This class method
        performs some sanity checks on the arguments, and is preferred
        over using a manually constructed ``lambda``.

        The first argument must be a protocol factory for a
        ``FramedProtocol`` object.  Subsequent positional and keyword
        arguments are interpreted as for the ``set_framer()`` method,
        which the proviso that both send and receive framers must be
        set after argument interpretation.

        :returns: A callable that returns an instance of
                  ``FramerProtocol``.
        """

        # Some basic sanity checks
        if not six.callable(client):
            raise exc.FramerException("Protocol factory is not a factory")

        # Cannot specify both positional and keyword arguments, but
        # must provide one or the other
        if not args and not kwargs:
            raise exc.InvalidFramerSpecification(
                "No framers specified")
        elif args and kwargs:
            raise exc.InvalidFramerSpecification(
                "Cannot mix positional and keyword framer specifications")

        # And a final, basic sanity check on the argument structure
        if not args and ('send' not in kwargs or 'recv' not in kwargs):
            raise exc.InvalidFramerSpecification(
                "Both send and receive framers must be specified")

        return lambda: cls(client, *args, **kwargs)

    def __init__(self, client, *args, **kwargs):
        """
        Initialize a ``FramerProtocol`` instance.

        The first argument must be a protocol factory for a
        ``FramedProtocol`` object.  Subsequent positional and keyword
        arguments are interpreted as for the ``set_framer()`` method,
        which the proviso that both send and receive framers must be
        set after argument interpretation.

        :returns: A callable that returns an instance of
                  ``FramerProtocol``.
        """

        # A basic sanity check
        if not six.callable(client):
            raise exc.FramerException("Protocol factory is not a factory")

        # Initialize the framer stack for _interpret_framer()
        self._framers = [FramerElement(None, None, None, None)]

        # Interpret the framer arguments
        elem = self._interpret_framer(args, kwargs)
        if not elem.send or not elem.recv:
            raise exc.InvalidFramerSpecification(
                "Both send and receive framers must be specified")

        # Set the framers
        self._framers = [elem]

        # Instantiate and save the client protocol, now that we have
        # framers
        self._client = client()

        # Remember the underlying transport
        self._transport = None

        # And initialize the receive buffer and read paused state
        self._recv_buf = bytearray()
        self._recv_paused = False

    def _interpret_framer(self, args, kwargs):
        """
        Interprets positional and keyword arguments related to
        framers.

        :param args: A tuple of positional arguments.  The first such
                     argument will be interpreted as a framer object,
                     and the second will be interpreted as a framer
                     state.
        :param kwargs: A dictionary of keyword arguments.  The
                       ``send`` and ``recv`` keyword arguments are
                       interpreted as send and receive framers,
                       respectively, and the ``send_state`` and
                       ``recv_state`` keyword arguments are
                       interpreted as states for those framers.

        :returns: An instance of ``FramerElement``, which may be
                  pushed onto the framer stack.
        """

        # Cannot specify both positional and keyword arguments, but
        # must provide one or the other
        if not args and not kwargs:
            raise exc.InvalidFramerSpecification(
                "No framers specified")
        elif args and kwargs:
            raise exc.InvalidFramerSpecification(
                "Cannot mix positional and keyword framer specifications")

        # Start with the current send and receive framers
        send = self._send_framer
        recv = self._recv_framer
        send_state = self._send_state
        recv_state = self._recv_state

        # Now, is it positional style?
        if args:
            send = args[0]
            recv = args[0]

            # Do we have a state?
            if len(args) > 1:
                send_state = args[1]
                recv_state = args[1]
            else:
                # Allocate one
                state = framers.FramerState()

                # Initialize it
                send.initialize_state(state)

                send_state = state
                recv_state = state
        else:
            # OK, it's keyword style; do we have a send framer?
            if 'send' in kwargs:
                send = kwargs['send']

                # Do we have a send state?
                if 'send_state' in kwargs:
                    send_state = kwargs['send_state']
                else:
                    # Allocate one and initialize it
                    send_state = framers.FramerState()
                    send.initialize_state(send_state)

            # How about a receive framer?
            if 'recv' in kwargs:
                recv = kwargs['recv']

                # Do we have a recv state?
                if 'recv_state' in kwargs:
                    recv_state = kwargs['recv_state']
                else:
                    # Allocate one and initialize it
                    recv_state = framers.FramerState()
                    recv.initialize_state(recv_state)

        # Create and return a FramerElement
        return FramerElement(send, recv, send_state, recv_state)

    def connection_made(self, transport):
        """
        Called by the underlying transport when a connection is made.

        :param transport: The transport representing the connection.
        """

        # Save the underlying transport
        self._transport = transport

        # Call connection_made() on the client protocol, passing
        # ourself as the transport
        self._client.connection_made(self)

    def connection_lost(self, exc):
        """
        Called by the underlying transport when a connection is lost.

        :param exc: Either an exception object or ``None``.  If the
                    latter, indicates an EOF was received, or that the
                    connection was aborted or closed by this side of
                    the connection.
        """

        # Call connection_lost() on the client protocol
        self._client.connection_lost(exc)

    def pause_writing(self):
        """
        Called by the underlying transport when the buffer goes over
        the high-water mark.
        """

        # Call pause_writing() on the client protocol
        self._client.pause_writing()

    def resume_writing(self):
        """
        Called by the underlying transport when the buffer drains
        below the low-water mark.
        """

        # Call resume_writing() on the client protocol
        self._client.resume_writing()

    def data_received(self, data):
        """
        Called by the underlying transport when data is received.

        :param data: The data received on the connection.
        """

        # First, add the data to the receive buffer
        self._recv_buf += data

        # Now, pass all frames we can find to the client protocol
        while self._recv_buf and not self._recv_paused:
            try:
                # Extract one frame
                frame = self._recv_framer.to_frame(self._recv_buf,
                                                   self._recv_state)
            except exc.NoFrames:
                # There's data in the buffer, but no complete frames
                break

            # Now call the client protocol's frame_received() method
            self._client.frame_received(frame)

    def eof_received(self):
        """
        Called by the underlying transport when the other end signals
        it won't send any more data.

        :returns: A ``False`` value (including ``None``, the default
                  return value) to cause the transport to close
                  itself, and ``True`` to leave the connection
                  half-open.
        """

        # Call eof_received() on the client protocol
        return self._client.eof_received()

    def close(self):
        """
        Called by the client protocol to close the connection.  If the
        transport has a buffer for outgoing data, buffered data will
        be flushed asynchronously.  No more data will be received.
        After all buffered data is flushed, the protocol's
        ``connection_lost()`` method will be called with ``None`` as
        its argument.
        """

        # Call close() on the transport
        self._transport.close()

    def get_extra_info(self, name, default=None):
        """
        Called by the client protocol to return optional transport
        information.  Information requests not recognized by the
        ``FramerProtocol`` are passed on to the underlying transport.

        The values of ``name`` recognized directly by
        ``FramerProtocol`` are:

        ===============  ============================================
        Value            Description
        ===============  ============================================
        send_framer      The active framer for the send direction.
        send_state       The state for the send framer.
        recv_framer      The active framer for the receive direction.
        recv_state       The state for the receive framer.
        recv_buf         The current receive buffer.
        recv_paused      ``True`` if reading is paused.
        client_protocol  The client ``FramedProtocol``.
        transport        The underlying transport.
        ===============  ============================================

        :param name: A string representing the piece of
                     transport-specific information to get.
        :param default: The value to return if the information doesn't
                        exist.

        :returns: The requested data.
        """

        # Handle data we know about
        if name in self._handlers:
            return self._handlers[name](self)

        # Call get_extra_info() on the transport
        return self._transport.get_extra_info(name, default=default)

    def pause_reading(self):
        """
        Called by the client protocol to pause the receiving end of
        the transport.  No data will be passed to the protocol's
        ``frame_received()`` method until ``resume_reading()`` is
        called.
        """

        # Remember that reading is paused
        self._recv_paused = True

        # Call pause_reading() on the transport
        self._transport.pause_reading()

    def resume_reading(self):
        """
        Called by the client protocol to resume the receiving end.
        The protocol's ``frame_received()`` method will be called once
        again if some data is available for reading.
        """

        # Clear the read pause status
        self._recv_paused = False

        # Call resume_reading() on the transport
        self._transport.resume_reading()

        # If there's data in the receive buffer, pass it on to the
        # client protocol
        if self._recv_buf:
            self.data_received(b'')

    def abort(self):
        """
        Called by the client protocol to close the transport
        immediately, without waiting for pending operations to
        complete.  Buffered data will be lost.  No more data will be
        received.  The protocol's ``connection_lost()`` method will
        eventually be called with ``None`` as its argument.
        """

        # Call abort() on the transport
        self._transport.abort()

    def can_write_eof(self):
        """
        Called by the client protocol to determine if the transport
        supports half-closed operations through the ``write_eof()``
        method.

        :returns: A ``True`` value if ``write_eof()`` is supported,
                  ``False`` otherwise.
        """

        # Call can_write_eof() on the transport
        return self._transport.can_write_eof()

    def get_write_buffer_size(self):
        """
        Called by the client protocol to return the current size of
        the output buffer used by the transport.

        :returns: The current size of the output buffer used by the
                  transport.
        """

        # Call get_write_buffer_size() on the transport
        return self._transport.get_write_buffer_size()

    def set_write_buffer_limits(self, high=None, low=None):
        """
        Called by the client protocol to set the high- and low-water
        limits for write flow control.

        These two values control when call the protocol's
        ``pause_writing()`` and ``resume_writing()`` methods are
        called.

        :param high: The high-water limit.  Must be a non-negative
                     integer greater than or equal to ``low``, if both
                     are specified.
        :param low: The low-water limit.  Must be a non-negative
                    integer less than or equal to ``high``, if both
                    are specified.  If only ``high`` is specified,
                    defaults to an implementation-specific value less
                    than or equal to ``high``.
        """

        # Call set_write_buffer_limits() on the transport
        self._transport.set_write_buffer_limits(high=high, low=low)

    def write_eof(self):
        """
        Called by the client protocol to close the write end of the
        transport after flushing buffered data.  Data may still be
        received.  This method may raise ``NotImplementedError`` if
        the transport (e.g., SSL) doesn't support half-closed
        connections.
        """

        # Call write_eof() on the transport
        self._transport.write_eof()

    def send_frame(self, frame):
        """
        Called by the client protocol to send a frame to the remote
        peer.  This method does not block; it buffers the data and
        arranges for it to be sent out asynchronously.

        :param frame: The frame to send to the peer.  Must be in the
                      format expected by the currently active send
                      framer.
        """

        # Convert the frame to bytes and write them to the connection
        data = self._send_framer.to_bytes(frame, self._send_state)
        self._transport.write(data)

    def push_framer(self, *args, **kwargs):
        """
        Called by the client protocol to temporarily switch to a new
        send framer, receive framer, or both.  Can be called multiple
        times.  Each call to ``push_framer()`` must be paired with a
        call to ``pop_framer()``, which restores to the previously set
        framer.

        When called with positional arguments, the first argument
        specifies a framer object to replace both send and receive
        framers.  A second argument may be used to specify a state
        object for the framers; if none is specified, a new one will
        be allocated and initialized by calling the appropriate framer
        initialization method.

        When called with keyword arguments, the ``send`` and ``recv``
        arguments specify the send and receive framer object,
        respectively.  If either is not provided, the existing framer
        for that direction will be maintained.  The ``send_state`` and
        ``recv_state`` arguments specify optional state objects for
        the respective framers, and will be allocated and initialized
        by calling the appropriate framer initialization method, if
        not provided.  If a state argument is given without a
        corresponding replacement framer, it will be ignored.
        """

        # First, interpret the arguments
        elem = self._interpret_framer(args, kwargs)

        # Append the element to the framer stack
        self._framers.append(elem)

    def pop_framer(self):
        """
        Called by the client protocol to revert to the set of framers
        in use prior to the corresponding ``push_framer()`` call.
        Raises an ``IndexError`` if the framer stack cannot be popped.
        """

        # If the framer stack has only one element, raise an
        # IndexError
        if len(self._framers) <= 1:
            raise IndexError('pop from empty stack')

        # Pop an element off
        self._framers.pop()

    def set_framer(self, *args, **kwargs):
        """
        Called by the client protocol to replace the current send
        framer, receive framer, or both.  This does not alter the
        stack maintained by ``push_framer()`` and ``pop_framer()``; if
        this method is called after ``push_framer()``, then
        ``pop_framer()`` is called, the framers in force at the time
        ``push_framer()`` was called will be restored.

        When called with positional arguments, the first argument
        specifies a framer object to replace both send and receive
        framers.  A second argument may be used to specify a state
        object for the framers; if none is specified, a new one will
        be allocated and initialized by calling the appropriate framer
        initialization method.

        When called with keyword arguments, the ``send`` and ``recv``
        arguments specify the send and receive framer object,
        respectively.  If either is not provided, the existing framer
        for that direction will be maintained.  The ``send_state`` and
        ``recv_state`` arguments specify optional state objects for
        the respective framers, and will be allocated and initialized
        by calling the appropriate framer initialization method, if
        not provided.  If a state argument is given without a
        corresponding replacement framer, it will be ignored.
        """

        # First, interpret the arguments
        elem = self._interpret_framer(args, kwargs)

        # Now, replace the current top of the framer stack
        self._framers[-1] = elem

    @property
    def _send_framer(self):
        """
        Retrieve the current send framer.
        """

        return self._framers[-1].send

    @property
    def _send_state(self):
        """
        Retrieve the current send framer state.
        """

        return self._framers[-1].send_state

    @property
    def _recv_framer(self):
        """
        Retrieve the current receive framer.
        """

        return self._framers[-1].recv

    @property
    def _recv_state(self):
        """
        Retrieve the current receive framer state.
        """

        return self._framers[-1].recv_state
