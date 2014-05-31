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
from framer import framers


class FramerStateTest(unittest.TestCase):
    def test_init(self):
        state = framers.FramerState()

        self.assertEqual(state._data, {})

    def test_getattr_available(self):
        state = framers.FramerState()
        state._data['test'] = 'value'

        self.assertEqual(state.test, 'value')

    def test_getattr_unavailable(self):
        state = framers.FramerState()
        state._data['test'] = 'value'

        self.assertRaises(AttributeError, lambda: state.other)

    def test_getitem_available(self):
        state = framers.FramerState()
        state._data['test'] = 'value'

        self.assertEqual(state['test'], 'value')

    def test_getitem_unavailable(self):
        state = framers.FramerState()
        state._data['test'] = 'value'

        self.assertRaises(KeyError, lambda: state['other'])

    def test_setattr_internal(self):
        state = framers.FramerState()

        state._attr = 'value'

        self.assertFalse('_attr' in state._data)
        self.assertTrue('_attr' in state.__dict__)
        self.assertEqual(state.__dict__['_attr'], 'value')

    def test_setattr_normal(self):
        state = framers.FramerState()

        state.attr = 'value'

        self.assertTrue('attr' in state._data)
        self.assertEqual(state._data, {'attr': 'value'})
        self.assertFalse('attr' in state.__dict__)

    def test_setitem_internal(self):
        state = framers.FramerState()

        def setter():
            state['_attr'] = 'value'

        self.assertRaises(KeyError, setter)
        self.assertFalse('_attr' in state.__dict__)
        self.assertFalse('_attr' in state._data)

    def test_setitem_normal(self):
        state = framers.FramerState()

        state['attr'] = 'value'

        self.assertEqual(state._data, {'attr': 'value'})

    def test_delattr_internal(self):
        state = framers.FramerState()
        state._attr = 'value'

        del state._attr

        self.assertFalse('_attr' in state.__dict__)

    def test_delattr_exists(self):
        state = framers.FramerState()
        state._data['attr'] = 'value'

        del state.attr

        self.assertEqual(state._data, {})

    def test_delattr_missing(self):
        state = framers.FramerState()

        def deleter():
            del state.attr

        self.assertRaises(AttributeError, deleter)

    def test_delitem_internal(self):
        state = framers.FramerState()
        state._data['_attr'] = 'value'

        def deleter():
            del state['_attr']

        self.assertRaises(KeyError, deleter)

    def test_delitem_exists(self):
        state = framers.FramerState()
        state._data['attr'] = 'value'

        del state['attr']

        self.assertEqual(state._data, {})

    def test_delitem_missing(self):
        state = framers.FramerState()

        def deleter():
            del state['attr']

        self.assertRaises(KeyError, deleter)

    def test_iter(self):
        state = framers.FramerState()
        state._data = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
        }

        result = set(iter(state))

        self.assertEqual(result, set('abcd'))

    def test_len(self):
        state = framers.FramerState()
        state._data = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
        }

        self.assertEqual(len(state), 4)


class IdentityFramerTest(unittest.TestCase):
    def test_to_frame(self):
        data = bytearray(b'this is a test')
        framer = framers.IdentityFramer()

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b''))

    def test_to_bytes(self):
        framer = framers.IdentityFramer()

        result = framer.to_bytes(bytearray(b'a frame'), None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'a frame')


class ChunkFramerTest(unittest.TestCase):
    def test_init(self):
        framer = framers.ChunkFramer(123)

        self.assertEqual(framer.chunk_len, 123)

    def test_initialize_state(self):
        framer = framers.ChunkFramer(123)
        state = framers.FramerState()

        framer.initialize_state(state)

        self.assertEqual(dict(state), {'chunk_remaining': 123})

    def test_to_frame_consumed(self):
        data = bytearray(b'this is a test')
        framer = framers.ChunkFramer(123)
        state = framers.FramerState()
        state.chunk_remaining = 0

        self.assertRaises(exc.NoFrames, framer.to_frame, data, state)
        self.assertEqual(data, bytearray(b'this is a test'))
        self.assertEqual(state.chunk_remaining, 0)

    def test_to_frame_moredata(self):
        data = bytearray(b'this is a test')
        framer = framers.ChunkFramer(123)
        state = framers.FramerState()
        state.chunk_remaining = 4

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this')
        self.assertEqual(data, bytearray(b' is a test'))
        self.assertEqual(state.chunk_remaining, 0)

    def test_to_frame_lessdata(self):
        data = bytearray(b'this is a test')
        framer = framers.ChunkFramer(123)
        state = framers.FramerState()
        state.chunk_remaining = 123

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b''))
        self.assertEqual(state.chunk_remaining, 109)

    def test_to_frame_exactdata(self):
        data = bytearray(b'this is a test')
        framer = framers.ChunkFramer(123)
        state = framers.FramerState()
        state.chunk_remaining = 14

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b''))
        self.assertEqual(state.chunk_remaining, 0)


class LineFramerTest(unittest.TestCase):
    def test_init_carriage_return(self):
        framer = framers.LineFramer()

        self.assertEqual(framer.carriage_return, True)
        self.assertEqual(framer.line_end, b'\r\n')

    def test_init_no_carriage_return(self):
        framer = framers.LineFramer(False)

        self.assertEqual(framer.carriage_return, False)
        self.assertEqual(framer.line_end, b'\n')

    def test_to_frame_partial(self):
        data = bytearray(b'this is a test')
        framer = framers.LineFramer()

        self.assertRaises(exc.NoFrames, framer.to_frame, data, None)
        self.assertEqual(data, bytearray(b'this is a test'))

    def test_to_frame_no_carriage_return_normal(self):
        data = bytearray(b'this is a test\nor something')
        framer = framers.LineFramer()

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b'or something'))

    def test_to_frame_with_carriage_return_normal(self):
        data = bytearray(b'this is a test\r\nor something')
        framer = framers.LineFramer()

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b'or something'))

    def test_to_frame_no_carriage_return_option(self):
        data = bytearray(b'this is a test\nor something')
        framer = framers.LineFramer(False)

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(data, bytearray(b'or something'))

    def test_to_frame_with_carriage_return_option(self):
        data = bytearray(b'this is a test\r\nor something')
        framer = framers.LineFramer(False)

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test\r')
        self.assertEqual(data, bytearray(b'or something'))

    def test_to_bytes_normal(self):
        framer = framers.LineFramer()

        result = framer.to_bytes(bytearray(b'this is a test'), None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test\r\n')

    def test_to_bytes_option(self):
        framer = framers.LineFramer(False)

        result = framer.to_bytes(bytearray(b'this is a test'), None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test\n')


class TrialFramer(framers.LengthEncodedFramer):
    def __init__(self):
        self._calls = []

    def encode_length(self, frame, state):
        self._calls.append(('encode_length', frame, state))
        return ('%04d' % len(frame)).encode('utf-8')

    def decode_length(self, data, state):
        self._calls.append(('decode_length', data, state))
        if len(data) < 4:
            raise exc.NoFrames()
        length = int(data[:4])
        del data[:4]
        return length


class LengthEncodedFramerTest(unittest.TestCase):
    def test_initialize_state(self):
        framer = TrialFramer()
        state = framers.FramerState()

        framer.initialize_state(state)

        self.assertEqual(dict(state), {'length': None})

    def test_to_frame_nohanglen_short(self):
        data = bytearray(b'0014this is a tes')
        framer = TrialFramer()
        state = framers.FramerState()
        framer.initialize_state(state)

        self.assertRaises(exc.NoFrames, framer.to_frame, data, state)
        self.assertEqual(dict(state), {'length': 14})
        self.assertEqual(data, bytearray(b'this is a tes'))
        self.assertEqual(framer._calls, [
            ('decode_length', data, state),
        ])

    def test_to_frame_nohanglen_complete(self):
        data = bytearray(b'0014this is a test!')
        framer = TrialFramer()
        state = framers.FramerState()
        framer.initialize_state(state)

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is a test')
        self.assertEqual(dict(state), {'length': None})
        self.assertEqual(data, bytearray(b'!'))
        self.assertEqual(framer._calls, [
            ('decode_length', data, state),
        ])

    def test_to_frame_hanglen_short(self):
        data = bytearray(b'0014this is a tes')
        framer = TrialFramer()
        state = framers.FramerState()
        framer.initialize_state(state)
        state.length = 18

        self.assertRaises(exc.NoFrames, framer.to_frame, data, state)
        self.assertEqual(dict(state), {'length': 18})
        self.assertEqual(data, bytearray(b'0014this is a tes'))
        self.assertEqual(framer._calls, [])

    def test_to_frame_hanglen_complete(self):
        data = bytearray(b'0014this is a test!')
        framer = TrialFramer()
        state = framers.FramerState()
        framer.initialize_state(state)
        state.length = 18

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'0014this is a test')
        self.assertEqual(dict(state), {'length': None})
        self.assertEqual(data, bytearray(b'!'))
        self.assertEqual(framer._calls, [])

    def test_to_bytes(self):
        framer = TrialFramer()

        result = framer.to_bytes(bytearray(b'this is a test'), None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'0014this is a test')
        self.assertEqual(framer._calls, [
            ('encode_length', bytearray(b'this is a test'), None),
        ])


class StructFramerTest(unittest.TestCase):
    @mock.patch('struct.Struct', return_value='struct')
    def test_init_unrecognized(self, mock_Struct):
        self.assertRaises(ValueError, framers.StructFramer, '@=<>!xz')
        self.assertFalse(mock_Struct.called)

    @mock.patch('struct.Struct', return_value='struct')
    def test_init_nospec(self, mock_Struct):
        self.assertRaises(ValueError, framers.StructFramer, '@=<>!x')
        self.assertFalse(mock_Struct.called)

    @mock.patch('struct.Struct', return_value='struct')
    def test_init_doublespec(self, mock_Struct):
        self.assertRaises(ValueError, framers.StructFramer, '@=<>!xII')
        self.assertFalse(mock_Struct.called)

    @mock.patch('struct.Struct', return_value='struct')
    def test_init_acceptable(self, mock_Struct):
        result = framers.StructFramer('@=<>!xI')

        self.assertEqual(result.fmt, 'struct')
        mock_Struct.assert_called_once_with('@=<>!xI')

    def test_encode_length(self):
        framer = framers.StructFramer('!B')

        result = framer.encode_length(b'this is a test', None)

        self.assertEqual(result, b'\x0e')

    def test_decode_length_short(self):
        data = bytearray(b'\x00')
        framer = framers.StructFramer('!H')

        self.assertRaises(exc.NoFrames, framer.decode_length, data, None)
        self.assertEqual(data, bytearray(b'\x00'))

    def test_decode_length_long(self):
        data = bytearray(b'\x00\x0ethis is a test')
        framer = framers.StructFramer('!H')

        result = framer.decode_length(data, None)

        self.assertEqual(result, 14)
        self.assertEqual(data, bytearray(b'this is a test'))


class StuffingFramerTest(unittest.TestCase):
    def test_init_empty_args(self):
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'', b'abc2', b'abc3')
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'', b'abc3')
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc2', b'')

    def test_init_bad_pfx(self):
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'bcd2', b'cde3')

    def test_init_mismatched_len(self):
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc', b'abc2', b'abc3')
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc', b'abc3')
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc2', b'abc')

    def test_init_indistinct_nop(self):
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc2', b'abc1')
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc2', b'abc2')

    def test_init_indistinct_begin_end(self):
        self.assertRaises(ValueError, framers.StuffingFramer,
                          b'abc1', b'abc1', b'abc3')

    def test_init(self):
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')

        self.assertEqual(framer.begin, b'abc1')
        self.assertEqual(framer.end, b'abc2')
        self.assertEqual(framer.nop, b'abc3')
        self.assertEqual(framer.prefix, b'abc')

    def test_initialize_state(self):
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')
        state = framers.FramerState()

        framer.initialize_state(state)

        self.assertEqual(dict(state), {'frame_start': False})

    def test_to_frame_nostart(self):
        data = bytearray(b'this is a testabc2')
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')
        state = framers.FramerState()
        framer.initialize_state(state)

        self.assertRaises(exc.NoFrames, framer.to_frame, data, state)
        self.assertEqual(dict(state), {'frame_start': False})
        self.assertEqual(data, bytearray(b'this is a testabc2'))

    def test_to_frame_withstart_noend(self):
        data = bytearray(b'ignorable paddingabc1this is a testabc')
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')
        state = framers.FramerState()
        framer.initialize_state(state)

        self.assertRaises(exc.NoFrames, framer.to_frame, data, state)
        self.assertEqual(dict(state), {'frame_start': True})
        self.assertEqual(data, bytearray(b'this is a testabc'))

    def test_to_frame_withstart(self):
        data = bytearray(b'ignorable paddingabc1this is abc3 a abc3 testabc2'
                         b'trailer')
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')
        state = framers.FramerState()
        framer.initialize_state(state)

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'this is abc a abc test')
        self.assertEqual(dict(state), {'frame_start': False})
        self.assertEqual(data, bytearray(b'trailer'))

    def test_to_frame_previous_start(self):
        data = bytearray(b'abc1this is abc3 a abc3 testabc2trailer')
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')
        state = framers.FramerState()
        framer.initialize_state(state)
        state.frame_start = True

        result = framer.to_frame(data, state)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'abc1this is abc a abc test')
        self.assertEqual(dict(state), {'frame_start': False})
        self.assertEqual(data, bytearray(b'trailer'))

    def test_to_bytes(self):
        framer = framers.StuffingFramer(b'abc1', b'abc2', b'abc3')

        result = framer.to_bytes(
            bytearray(b'this abc1 is abc2 a abc3 test abc'), None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result,
                         b'abc1this abc31 is abc32 a abc33 test abc3abc2')


class COBSFramerTest(unittest.TestCase):
    def test_init_default(self):
        framer = framers.COBSFramer()

        self.assertEqual(framer.variant, framers.COBSFramer.VARIANT_COBS)

    def test_init(self):
        framer = framers.COBSFramer('variant')

        self.assertEqual(framer.variant, 'variant')

    def test_to_frame_partial(self):
        data = bytearray(b'this is a test')
        variant = mock.Mock(**{'decode.return_value': bytearray(b'test')})
        framer = framers.COBSFramer(variant)

        self.assertRaises(exc.NoFrames, framer.to_frame, data, None)
        self.assertEqual(data, bytearray(b'this is a test'))
        self.assertFalse(variant.decode.called)

    def test_to_frame_complete(self):
        data = bytearray(b'this is a test\0trailer')
        variant = mock.Mock(**{'decode.return_value': bytearray(b'test')})
        framer = framers.COBSFramer(variant)

        result = framer.to_frame(data, None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'test')
        self.assertEqual(data, bytearray(b'trailer'))
        variant.decode.assert_called_once_with(b'this is a test')

    def test_to_bytes(self):
        variant = mock.Mock(**{'encode.return_value': bytearray(b'test')})
        framer = framers.COBSFramer(variant)

        result = framer.to_bytes(b'this is a test', None)

        self.assertTrue(isinstance(result, six.binary_type))
        self.assertEqual(result, b'test\0')
