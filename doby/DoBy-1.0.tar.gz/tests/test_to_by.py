
# Copyright (c) 2014.
# See LICENSE for more details

"""
Tests for do_by
"""

import unittest
from datetime import datetime, timedelta

from do_by import TODO, DoBy


class TODOTest(unittest.TestCase):

    def setUp(self):
        self.now = datetime.now()

    def test_now_plus_a_day(self):
        delta = timedelta(days=1)
        TODO('Test TODO', self.now + delta)

    def test_raises_exception(self):
        self._raise_doby_exception(self.now)

    def test_using_string(self):
        TODO('Test TODO', '2034-10-12')

    def test_using_string_with_time(self):
        TODO('Test TODO', '2034-10-12 20:00')

    def test_using_string_raises_exception(self):
        self._raise_doby_exception('2004-10-12')

    def test_using_string_with_time_raises_exception(self):
        self._raise_doby_exception('2004-10-12 20:00')

    def _raise_doby_exception(self, do_by):
        try:
            TODO('Test TODO', do_by)
        except DoBy:
            self.assertTrue(True, 'DoBy raised because time passed TODO')
        except Exception:
            raise
