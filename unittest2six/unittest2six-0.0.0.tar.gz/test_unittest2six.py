from __future__ import with_statement

import unittest2 as unittest


class TestStuff(unittest.TestCase):
    def test_assertRaises_context_manager(self):
        with self.assertRaises(RuntimeError) as context:
            raise RuntimeError('foo')
        self.assertEqual(str(context.exception), 'foo')

    def test_assertIsInstance(self):
        self.assertIsInstance(self, unittest.TestCase)

    def test_assertNotIsInstance(self):
        self.assertNotIsInstance(1, unittest.TestCase)

    def test_assertIsNone(self):
        self.assertIsNone(None)

    def test_assertIsNotNone(self):
        self.assertIsNotNone(1)

    def test_assertIn(self):
        self.assertIn(1, [1, 2, 3])

    def test_assertNotIn(self):
        self.assertNotIn(4, [1, 2, 3])

    def test_assertRaisesRegexp(self):
        with self.assertRaisesRegexp(ValueError, 'literal'):
            int('XYZ')

    @unittest.skip("demonstrating skipping")
    def test_skipping(self):
        self.fail("shouldn't happen")
