# -*- coding: utf-8 -*-

import unittest

from ..message import Message

class TestMessage(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        m = Message()
        self.assertIsNotNone(m)

    def test_single_key(self):
        m = Message()
        m.set_task_obj("mytask", 100, "my", "key")
        self.assertEqual(m.get_task_obj("mytask", 100), { "my": "key" })

    def test_replacement_key(self):
        m = Message()
        m.set_task_obj("mytask", 100, "my", "key")
        self.assertEqual(m.get_task_obj("mytask", 100), { "my": "key" })
        m.set_task_obj("mytask", 100, "my", "key2")
        self.assertEqual(m.get_task_obj("mytask", 100), { "my": "key2" })

    def test_missing_task(self):
        m = Message()
        try:
            m.get_task_obj("mytask", 200)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_missing_val(self):
        m = Message()
        m.set_task_obj("mytask", 300, "my", "key")
        try:
            m.get_task_obj("mytask", 1)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_empty_key(self):
        m = Message()
        try:
            m.set_task_obj(None, 200, "my", "key")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_empty_obj_id(self):
        m = Message()
        try:
            m.set_task_obj("task", None, "my", "key")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_empty_key(self):
        m = Message()
        try:
            m.set_task_obj("task", 200, None, "key")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_unicode(self):
        task = "タスク"
        obj_id = "番号"
        key = "俺"
        val = "鍵"

        m = Message()

        m.set_task_obj(task, obj_id, key, val)
        task = m.get_task_obj(task, obj_id)
        self.assertEqual(task[key], val)
