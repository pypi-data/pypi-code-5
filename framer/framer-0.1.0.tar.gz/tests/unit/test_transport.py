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

import unittest

import mock
import six

from framer import exc
from framer import transport


class FramerAdaptorTest(unittest.TestCase):
    def test_extra_info_handlers(self):
        obj = mock.Mock(
            _send_framer='send_framer',
            _send_state='send_state',
            _recv_framer='recv_framer',
            _recv_state='recv_state',
            _recv_buf=bytearray(b'recv_buf'),
            _recv_paused='recv_paused',
            _client='client_protocol',
            _transport='transport',
        )

        for key in ('send_framer', 'send_state', 'recv_framer', 'recv_state',
                    'recv_paused', 'client_protocol', 'transport'):
            self.assertEqual(transport.FramerAdaptor._handlers[key](obj), key)

        # Cover recv_buf a little specially
        result = transport.FramerAdaptor._handlers['recv_buf'](obj)
        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'recv_buf')

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_noncallable(self, mock_init):
        self.assertRaises(exc.FramerException, transport.FramerAdaptor.factory,
                          'noncallable', 'a', 'b', 'c')
        self.assertFalse(mock_init.called)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_noargs(self, mock_init):
        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor.factory, lambda: None)
        self.assertFalse(mock_init.called)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_allargs(self, mock_init):
        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor.factory, lambda: None,
                          'a', 'b', 'c', d=4, e=5, f=6)
        self.assertFalse(mock_init.called)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_nosend(self, mock_init):
        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor.factory, lambda: None,
                          recv='framer')
        self.assertFalse(mock_init.called)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_norecv(self, mock_init):
        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor.factory, lambda: None,
                          send='framer')
        self.assertFalse(mock_init.called)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_positional(self, mock_init):
        client = lambda: None

        result = transport.FramerAdaptor.factory(client, 'framer')

        self.assertTrue(six.callable(result))
        self.assertFalse(mock_init.called)

        result2 = result()

        self.assertTrue(isinstance(result2, transport.FramerAdaptor))
        mock_init.assert_called_once_with(client, 'framer')

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def test_factory_keyword(self, mock_init):
        client = lambda: None

        result = transport.FramerAdaptor.factory(client, send='send',
                                                 recv='recv')

        self.assertTrue(six.callable(result))
        self.assertFalse(mock_init.called)

        result2 = result()

        self.assertTrue(isinstance(result2, transport.FramerAdaptor))
        mock_init.assert_called_once_with(client, send='send', recv='recv')

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement('send', 'recv',
                                                            None, None))
    def test_init_noncallable(self, mock_interpret_framer):
        self.assertRaises(exc.FramerException, transport.FramerAdaptor,
                          'noncallable', 'a', 'b', 'c')
        self.assertFalse(mock_interpret_framer.called)

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement(None, 'recv',
                                                            None, None))
    def test_init_nosend(self, mock_interpret_framer):
        client = mock.Mock(return_value='client')

        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor, client, 'a', 'b', c=3, d=4)
        mock_interpret_framer.assert_called_once_with(
            ('a', 'b'), {'c': 3, 'd': 4})
        self.assertFalse(client.called)

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement('send', None,
                                                            None, None))
    def test_init_norecv(self, mock_interpret_framer):
        client = mock.Mock(return_value='client')

        self.assertRaises(exc.InvalidFramerSpecification,
                          transport.FramerAdaptor, client, 'a', 'b', c=3, d=4)
        mock_interpret_framer.assert_called_once_with(
            ('a', 'b'), {'c': 3, 'd': 4})
        self.assertFalse(client.called)

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement('send', 'recv',
                                                            None, None))
    def test_init_normal(self, mock_interpret_framer):
        client = mock.Mock(return_value='client')

        result = transport.FramerAdaptor(client, 'a', 'b', c=3, d=4)

        self.assertEqual(result._framers, [mock_interpret_framer.return_value])
        self.assertEqual(result._client, 'client')
        self.assertEqual(result._transport, None)
        self.assertTrue(isinstance(result._recv_buf, bytearray))
        self.assertEqual(result._recv_buf, bytearray())
        self.assertEqual(result._recv_paused, False)

    @mock.patch.object(transport.FramerAdaptor, '__init__', return_value=None)
    def make_adaptor(self, mock_init, **kwargs):
        adaptor = transport.FramerAdaptor()

        # Set up the basic information
        adaptor._framers = kwargs.get('framers', [
            transport.FramerElement('send', 'recv', 'send_state', 'recv_state')
        ])
        adaptor._client = kwargs.get('client', 'client')
        adaptor._transport = kwargs.get('transport', None)
        adaptor._recv_buf = bytearray(kwargs.get('recv_buf', b''))
        adaptor._recv_paused = kwargs.get('recv_paused', False)

        return adaptor

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_noargs(self, mock_FramerState):
        adaptor = self.make_adaptor()

        self.assertRaises(exc.InvalidFramerSpecification,
                          adaptor._interpret_framer, (), {})
        self.assertFalse(mock_FramerState.called)

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_allargs(self, mock_FramerState):
        adaptor = self.make_adaptor()

        self.assertRaises(exc.InvalidFramerSpecification,
                          adaptor._interpret_framer, ('positional',), {
                              'send': mock.Mock(),
                              'recv': mock.Mock(),
                          })
        self.assertFalse(mock_FramerState.called)

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_positional_nostate(self, mock_FramerState):
        framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((framer,), {})

        self.assertEqual(result, (framer, framer,
                                  'framer_state', 'framer_state'))
        mock_FramerState.assert_called_once_with()
        framer.initialize_state.assert_called_once_with('framer_state')

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_positional_withstate(self, mock_FramerState):
        framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((framer, 'my_state'), {})

        self.assertEqual(result, (framer, framer, 'my_state', 'my_state'))
        self.assertFalse(mock_FramerState.called)
        self.assertFalse(framer.initialize_state.called)

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_keyword_sendonly(self, mock_FramerState):
        send_framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((), {
            'send': send_framer,
            'recv_state': 'ignored',
        })

        self.assertEqual(result, (send_framer, 'recv',
                                  'framer_state', 'recv_state'))
        mock_FramerState.assert_called_once_with()
        send_framer.initialize_state.assert_called_once_with('framer_state')

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_keyword_send_withstate(self, mock_FramerState):
        send_framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((), {
            'send': send_framer,
            'send_state': 'my_state',
            'recv_state': 'ignored',
        })

        self.assertEqual(result, (send_framer, 'recv',
                                  'my_state', 'recv_state'))
        self.assertFalse(mock_FramerState.called)
        self.assertFalse(send_framer.initialize_state.called)

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_keyword_recvonly(self, mock_FramerState):
        recv_framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((), {
            'recv': recv_framer,
            'send_state': 'ignored',
        })

        self.assertEqual(result, ('send', recv_framer,
                                  'send_state', 'framer_state'))
        mock_FramerState.assert_called_once_with()
        recv_framer.initialize_state.assert_called_once_with('framer_state')

    @mock.patch('framer.framers.FramerState', return_value='framer_state')
    @mock.patch.object(transport.FramerAdaptor, '_send_framer', 'send')
    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', 'recv')
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'send_state')
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'recv_state')
    def test_interpret_framer_keyword_recv_withstate(self, mock_FramerState):
        recv_framer = mock.Mock()
        adaptor = self.make_adaptor()

        result = adaptor._interpret_framer((), {
            'recv': recv_framer,
            'recv_state': 'my_state',
            'send_state': 'ignored',
        })

        self.assertEqual(result, ('send', recv_framer,
                                  'send_state', 'my_state'))
        self.assertFalse(mock_FramerState.called)
        self.assertFalse(recv_framer.initialize_state.called)

    def test_connection_made(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client)

        adaptor.connection_made('transport')

        self.assertEqual(adaptor._transport, 'transport')
        client.connection_made.assert_called_once_with(adaptor)

    def test_connection_lost(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client)

        adaptor.connection_lost('exception')

        client.connection_lost.assert_called_once_with('exception')

    def test_pause_writing(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client)

        adaptor.pause_writing()

        client.pause_writing.assert_called_once_with()

    def test_resume_writing(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client)

        adaptor.resume_writing()

        client.resume_writing.assert_called_once_with()

    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', mock.Mock(**{
        'to_frame.return_value': 'a frame',
    }))
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'state')
    def test_data_received_paused(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client, recv_paused=True)

        adaptor.data_received(b'this is a test')

        self.assertFalse(adaptor._recv_framer.to_frame.called)
        self.assertFalse(client.frame_received.called)

    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', mock.Mock(**{
        'to_frame.return_value': 'a frame',
    }))
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'state')
    def test_data_received_emptybuf(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client)

        adaptor.data_received(b'')

        self.assertFalse(adaptor._recv_framer.to_frame.called)
        self.assertFalse(client.frame_received.called)

    @mock.patch.object(transport.FramerAdaptor, '_recv_framer', mock.Mock(**{
        'to_frame.side_effect': [
            'a frame',
            exc.NoFrames(),
        ],
    }))
    @mock.patch.object(transport.FramerAdaptor, '_recv_state', 'state')
    def test_data_received(self):
        client = mock.Mock()
        adaptor = self.make_adaptor(client=client, recv_buf=b'this is')

        adaptor.data_received(b' a test')

        adaptor._recv_framer.to_frame.assert_has_calls([
            mock.call(bytearray(b'this is a test'), 'state'),
            mock.call(bytearray(b'this is a test'), 'state'),
        ])
        self.assertEqual(adaptor._recv_framer.to_frame.call_count, 2)
        client.frame_received.assert_called_once_with('a frame')

    def test_eof_received(self):
        client = mock.Mock(**{'eof_received.return_value': 'continue'})
        adaptor = self.make_adaptor(client=client)

        result = adaptor.eof_received()

        self.assertEqual(result, 'continue')
        client.eof_received.assert_called_once_with()

    def test_close(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.close()

        trans.close.assert_called_once_with()

    @mock.patch.dict(transport.FramerAdaptor._handlers, clear=True,
                     other=mock.Mock(return_value='result'))
    def test_get_extra_info_ours(self):
        trans = mock.Mock(**{'get_extra_info.return_value': 'info'})
        adaptor = self.make_adaptor(transport=trans)

        result = adaptor.get_extra_info('other')

        self.assertEqual(result, 'result')
        self.assertFalse(trans.get_extra_info.called)

    @mock.patch.dict(transport.FramerAdaptor._handlers, clear=True,
                     other=mock.Mock(return_value='result'))
    def test_get_extra_info_transport(self):
        trans = mock.Mock(**{'get_extra_info.return_value': 'info'})
        adaptor = self.make_adaptor(transport=trans)

        result = adaptor.get_extra_info('something')

        self.assertEqual(result, 'info')
        trans.get_extra_info.assert_called_once_with('something',
                                                     default=None)

    @mock.patch.dict(transport.FramerAdaptor._handlers, clear=True,
                     other=mock.Mock(return_value='result'))
    def test_get_extra_info_transport_default(self):
        trans = mock.Mock(**{'get_extra_info.return_value': 'info'})
        adaptor = self.make_adaptor(transport=trans)

        result = adaptor.get_extra_info('something', 'default')

        self.assertEqual(result, 'info')
        trans.get_extra_info.assert_called_once_with('something',
                                                     default='default')

    def test_pause_reading(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.pause_reading()

        self.assertEqual(adaptor._recv_paused, True)
        trans.pause_reading.assert_called_once_with()

    @mock.patch.object(transport.FramerAdaptor, 'data_received')
    def test_resume_reading_emptybuf(self, mock_data_received):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans, recv_paused=True)

        adaptor.resume_reading()

        self.assertEqual(adaptor._recv_paused, False)
        trans.resume_reading.assert_called_once_with()
        self.assertFalse(mock_data_received.called)

    @mock.patch.object(transport.FramerAdaptor, 'data_received')
    def test_resume_reading_nonemptybuf(self, mock_data_received):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans, recv_paused=True,
                                    recv_buf=b'this is a test')

        adaptor.resume_reading()

        self.assertEqual(adaptor._recv_paused, False)
        trans.resume_reading.assert_called_once_with()
        mock_data_received.assert_called_once_with(b'')

    def test_abort(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.abort()

        trans.abort.assert_called_once_with()

    def test_can_write_eof(self):
        trans = mock.Mock(**{'can_write_eof.return_value': 'can_eof'})
        adaptor = self.make_adaptor(transport=trans)

        result = adaptor.can_write_eof()

        self.assertEqual(result, 'can_eof')
        trans.can_write_eof.assert_called_once_with()

    def test_get_write_buffer_size(self):
        trans = mock.Mock(**{'get_write_buffer_size.return_value': 1024})
        adaptor = self.make_adaptor(transport=trans)

        result = adaptor.get_write_buffer_size()

        self.assertEqual(result, 1024)
        trans.get_write_buffer_size.assert_called_once_with()

    def test_set_write_buffer_limits_noargs(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.set_write_buffer_limits()

        trans.set_write_buffer_limits.assert_called_once_with(
            high=None, low=None)

    def test_set_write_buffer_limits_withargs(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.set_write_buffer_limits(1024, 512)

        trans.set_write_buffer_limits.assert_called_once_with(
            high=1024, low=512)

    def test_write_eof(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.write_eof()

        trans.write_eof.assert_called_once_with()

    @mock.patch.object(transport.FramerAdaptor, '_send_framer', mock.Mock(**{
        'to_bytes.return_value': b'some bytes',
    }))
    @mock.patch.object(transport.FramerAdaptor, '_send_state', 'state')
    def test_send_frame(self):
        trans = mock.Mock()
        adaptor = self.make_adaptor(transport=trans)

        adaptor.send_frame('a frame')

        adaptor._send_framer.to_bytes.assert_called_once_with(
            'a frame', 'state')
        trans.write.assert_called_once_with(b'some bytes')

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement('new_send',
                                                            'new_recv',
                                                            'new_send_state',
                                                            'new_recv_state'))
    def test_push_framer(self, mock_interpret_framer):
        adaptor = self.make_adaptor()

        adaptor.push_framer('a', 'b', c=3, d=4)

        self.assertEqual(adaptor._framers, [
            ('send', 'recv', 'send_state', 'recv_state'),
            ('new_send', 'new_recv', 'new_send_state', 'new_recv_state'),
        ])
        mock_interpret_framer.assert_called_once_with(
            ('a', 'b'), {'c': 3, 'd': 4})

    def test_pop_framer_empty(self):
        adaptor = self.make_adaptor()

        self.assertRaises(IndexError, adaptor.pop_framer)

        self.assertEqual(adaptor._framers, [
            ('send', 'recv', 'send_state', 'recv_state'),
        ])

    def test_pop_framer_nonempty(self):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        adaptor.pop_framer()

        self.assertEqual(adaptor._framers, [
            ('send1', 'recv1', 'send1_state', 'recv1_state'),
            ('send2', 'recv2', 'send2_state', 'recv2_state'),
        ])

    @mock.patch.object(transport.FramerAdaptor, '_interpret_framer',
                       return_value=transport.FramerElement('new_send',
                                                            'new_recv',
                                                            'new_send_state',
                                                            'new_recv_state'))
    def test_set_framer(self, mock_interpret_framer):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        adaptor.set_framer('a', 'b', c=3, d=4)

        self.assertEqual(adaptor._framers, [
            ('send1', 'recv1', 'send1_state', 'recv1_state'),
            ('send2', 'recv2', 'send2_state', 'recv2_state'),
            ('new_send', 'new_recv', 'new_send_state', 'new_recv_state'),
        ])
        mock_interpret_framer.assert_called_once_with(
            ('a', 'b'), {'c': 3, 'd': 4})

    def test_send_framer(self):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        self.assertEqual(adaptor._send_framer, 'send3')

    def test_send_state(self):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        self.assertEqual(adaptor._send_state, 'send3_state')

    def test_recv_framer(self):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        self.assertEqual(adaptor._recv_framer, 'recv3')

    def test_recv_state(self):
        adaptor = self.make_adaptor(framers=[
            transport.FramerElement('send1', 'recv1',
                                    'send1_state', 'recv1_state'),
            transport.FramerElement('send2', 'recv2',
                                    'send2_state', 'recv2_state'),
            transport.FramerElement('send3', 'recv3',
                                    'send3_state', 'recv3_state'),
        ])

        self.assertEqual(adaptor._recv_state, 'recv3_state')
