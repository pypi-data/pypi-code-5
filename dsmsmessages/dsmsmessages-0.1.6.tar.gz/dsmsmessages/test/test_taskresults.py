# -*- coding: utf-8 -*-

import unittest

from ..taskresults import TaskResults
from ..taskresult import TaskResult

class TestMessage(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        m = TaskResults()
        self.assertIsNotNone(m)

    def test_single_key(self):
        m = TaskResults()
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("mytest", "result")
        tr.finish()
        m.add_task_result(tr)

        # now extract the test
        tr_extract = m.get_task_result("mytask", 100)
        self.assertIsNotNone(tr_extract)
        self.assertEqual(tr_extract.success, True)
        self.assertEqual(tr_extract.get_data("mytest"), "result")

    def test_replacement_key(self):
        # check we can overwrite an old result with a new one
        m = TaskResults()
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("mytest", "result")
        tr.finish()
        m.add_task_result(tr)

        tr2 = TaskResult("mytask", "1.1.1", 100)
        tr2.add("mytest", "result2")
        tr2.finish()
        m.add_task_result(tr2)

         # now extract the test
        tr_extract = m.get_task_result("mytask", 100)
        self.assertIsNotNone(tr_extract)
        self.assertEqual(tr_extract.success, True)
        self.assertEqual(tr_extract.get_data("mytest"), "result2")

    def test_missing_task(self):
        m = TaskResults()
        try:
            tr_extract = m.get_task_result("mytask", 100)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_missing_val(self):
        m = TaskResults()
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("mytest", "result")
        tr.finish()
        m.add_task_result(tr)

        try:
            tr_extract = m.get_task_result("mytask", 999)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_unicode(self):
        task = "タスク"
        key = "俺"
        val = "鍵"

        m = TaskResults()
        tr = TaskResult(task, "1.1.1", 100)
        tr.add(key, val)
        tr.finish()
        m.add_task_result(tr)

        tr_extract = m.get_task_result(task, 100)

        self.assertEqual(tr_extract.get_data(key), val)

    def test_task_loop(self):
        m = TaskResults()
        tr = TaskResult("task1", "1.1.1", 100)
        tr.add("result1", [1, 2, 3])
        tr.add("result2", [1, 2, 3])
        tr.finish()

        tr2 = TaskResult("task2", "1.1.1", 100)
        tr.add("result2_1", "hello")
        tr.add("result2_1", "foo")
        tr.finish()

        m.add_task_result(tr)
        m.add_task_result(tr2)

        self.assertEqual(set(m.tasks()), set(["task1", "task2"]))

    def test_task_item_loop(self):
        m = TaskResults()
        tr = TaskResult("task1", "1.1.1", 100)
        tr.add("result1", [1, 2, 3])
        tr.add("result2", [1, 2, 3])
        tr.finish()

        tr2 = TaskResult("task2", "1.1.1", 100)
        tr.add("result2_1", "hello")
        tr.add("result2_1", "foo")
        tr.finish()

        m.add_task_result(tr)
        m.add_task_result(tr2)

        self.assertEqual(set(m.task_objs("task1")), set([100]))
