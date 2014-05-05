#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyxkcdpass
----------------------------------

Tests for `pyxkcdpass` module.
"""

import unittest

from pyxkcdpass import XKCDPass


class TestPyxkcdpass(unittest.TestCase):

    def setUp(self):
        self.length = 4
        self.dictionary_path = 'dictionary'
        self.password_generator = XKCDPass(self.dictionary_path, self.length)

    def test_lightning_strike_twice(self):
        self.assertNotEqual(self.password_generator.generate_random_password(), self.password_generator.generate_random_password())
        
    def test_generated_password_size(self):
        self.assertEqual( len(self.password_generator.generate_random_password().split()), self.length)
        
    def test_generate_password_custom_size(self):
        self.assertEqual( len(self.password_generator.generate_random_password(self.length+1).split()), self.length+1)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
