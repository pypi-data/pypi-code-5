# -*- coding:utf-8 -*-

import unittest2

from swf.utils import *


class TestUtils(unittest2.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_non_existent_subkey_from_first_level(self):
        base_dict = {
            'a': {
                '1': 2,
                '2': 3,
            }
        }

        self.assertIsNone(get_subkey(base_dict, 'b'))

    def test_get_existent_subkey_from_first_level(self):
        base_dict = {
            'a': {
                '1': 2,
                '2': 3,
            }
        }

        self.assertEqual(get_subkey(base_dict, 'a'), base_dict['a'])

    def test_get_non_existent_subkey_from_n_level(self):
        base_dict = {
            'a': {
                '1': 2,
                '2': 3,
            }
        }

        self.assertIsNone(get_subkey(base_dict, ['a', '3']))

    def test_get_existent_subkey_from_n_level(self):
        base_dict = {
            'a': {
                '1': 2,
                '2': 3,
            }
        }

        self.assertEqual(get_subkey(base_dict, ['a', '1']), 2)

    def test_get_existent_subkey_with_missing_parent_key(self):
        base_dict = {
            'a': {
                '1': 2,
                '2': 3,
            }
        }


        self.assertIsNone(get_subkey(base_dict, ['b', '1']))