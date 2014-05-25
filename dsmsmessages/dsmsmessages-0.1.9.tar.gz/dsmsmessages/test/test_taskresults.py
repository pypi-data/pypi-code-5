# -*- coding: utf-8 -*-

import unittest
import colander

from ..taskresults import TaskResults
from ..taskresult import TaskResult
from ..schemas import _BaseTaskSchema


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.task_name_1 = "test"

    def test_init(self):
        m = TaskResults()
        self.assertIsNotNone(m)

    def test_single_key(self):
        m = TaskResults()
        tr = TaskResult(self.task_name_1, "1.1.1", 100)
        tr.add("a", "result")
        tr.finish()
        m.add_task_result(tr)

        # now extract the test
        tr_extract = m.get_task_result(self.task_name_1, 100)
        self.assertIsNotNone(tr_extract)
        self.assertEqual(tr_extract.success, True)
        self.assertEqual(tr_extract.get_data("a"), "result")

    def test_replacement_key(self):
        # check we can overwrite an old result with a new one
        m = TaskResults()
        tr = TaskResult(self.task_name_1, "1.1.1", 100)
        tr.add("a", "result")
        tr.finish()
        m.add_task_result(tr)

        tr2 = TaskResult(self.task_name_1, "1.1.1", 100)
        tr2.add("a", "result2")
        tr2.finish()
        m.add_task_result(tr2)

        # now extract the test
        tr_extract = m.get_task_result(self.task_name_1, 100)
        self.assertIsNotNone(tr_extract)
        self.assertEqual(tr_extract.success, True)
        self.assertEqual(tr_extract.get_data("a"), "result2")

    def test_missing_task(self):
        m = TaskResults()
        try:
            m.get_task_result(self.task_name_1, 100)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_missing_val(self):
        m = TaskResults()
        tr = TaskResult(self.task_name_1, "1.1.1", 100)
        tr.add("a", "result")
        tr.finish()
        m.add_task_result(tr)

        try:
            m.get_task_result(self.task_name_1, 999)
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_unicode(self):
        task = "unicoder"
        key = u"俺"
        val = u"鍵"

        class UnicodeSchema(_BaseTaskSchema):
            z = colander.SchemaNode(colander.String(), name=key)

        m = TaskResults()
        tr = TaskResult(task, "1.1.1", 100, schema=UnicodeSchema)
        tr.add("a", "result")
        tr.add(key, val)
        tr.finish()
        m.add_task_result(tr)

        tr_extract = m.get_task_result(task, 100, schema=UnicodeSchema)

        self.assertEqual(tr_extract.get_data(key), val)

    def test_task_loop(self):

        class TaskLoop1Schema(_BaseTaskSchema):
            y = colander.SchemaNode(colander.List(), name="y")
            z = colander.SchemaNode(colander.List(), name="z")

        class TaskLoop2Schema(_BaseTaskSchema):
            y = colander.SchemaNode(colander.List(), name="y")
            z = colander.SchemaNode(colander.List(), name="z")

        m = TaskResults()
        tr = TaskResult("task1", "1.1.1", 100, schema=TaskLoop1Schema)
        tr.add("y", [1, 2, 3])
        tr.add("z", [1, 2, 3])
        tr.finish()

        tr2 = TaskResult("task2", "1.1.1", 100, schema=TaskLoop2Schema)
        tr.add("y", "hello")
        tr.add("z", "foo")
        tr.finish()

        m.add_task_result(tr)
        m.add_task_result(tr2)

        self.assertEqual(set(m.tasks()), set(["task1", "task2"]))

    def test_task_item_loop(self):

        class TaskLoop1Schema(_BaseTaskSchema):
            y = colander.SchemaNode(colander.List(), name="y")
            z = colander.SchemaNode(colander.List(), name="z")

        class TaskLoop2Schema(_BaseTaskSchema):
            y = colander.SchemaNode(colander.List(), name="y")
            z = colander.SchemaNode(colander.List(), name="z")

        m = TaskResults()
        tr = TaskResult("task1", "1.1.1", 100, schema=TaskLoop1Schema)
        tr.add("y", [1, 2, 3])
        tr.add("z", [1, 2, 3])
        tr.finish()

        tr2 = TaskResult("task2", "1.1.1", 100, schema=TaskLoop2Schema)
        tr.add("y", "hello")
        tr.add("z", "foo")
        tr.finish()

        m.add_task_result(tr)
        m.add_task_result(tr2)

        self.assertEqual(set(m.task_objs("task1")), set([100]))

    def test_task_multi_tmoid(self):

        class TaskLoop1Schema(_BaseTaskSchema):
            y = colander.SchemaNode(colander.List(), name="y")
            z = colander.SchemaNode(colander.List(), name="z")

        class TaskLoop2Schema(_BaseTaskSchema):
            a = colander.SchemaNode(colander.String(), name="a")
            b = colander.SchemaNode(colander.String(), name="b")

        m = TaskResults()
        tr = TaskResult("task1", "1.1.1", 100, schema=TaskLoop1Schema)
        tr.add("y", [1, 2, 3])
        tr.add("z", [1, 2, 3])
        tr.finish()

        tr2 = TaskResult("task1", "1.1.1", 101, schema=TaskLoop1Schema)
        tr2.add("y", [4, 5, 6])
        tr2.add("z", [7, 8, 9])
        tr2.finish()

        tr3 = TaskResult("task2", "1.1.1", 100, schema=TaskLoop2Schema)
        tr3.add("a", "hello")
        tr3.add("b", "foo")
        tr3.finish()

        m.add_task_result(tr)
        m.add_task_result(tr2)
        m.add_task_result(tr3)

        self.assertEqual(set(m.task_objs("task1")), set([100, 101]))

        tr_extract = m.get_task_result("task1", 100, schema=TaskLoop1Schema)
        tr2_extract = m.get_task_result("task1", 101, schema=TaskLoop1Schema)
        tr3_extract = m.get_task_result("task2", 100, schema=TaskLoop2Schema)

        self.assertEqual(tr_extract.get_data("y"), [1, 2, 3])
        self.assertEqual(tr_extract.get_data("z"), [1, 2, 3])
        self.assertEqual(tr2_extract.get_data("y"), [4, 5, 6])
        self.assertEqual(tr2_extract.get_data("z"), [7, 8, 9])
        self.assertEqual(tr3_extract.get_data("a"), "hello")
        self.assertEqual(tr3_extract.get_data("b"), "foo")
