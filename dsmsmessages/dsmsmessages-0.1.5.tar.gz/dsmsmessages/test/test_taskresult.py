# -*- coding: utf-8 -*-

import unittest
import json

from ..taskresult import TaskResult
from ..fields import MsgFields as F


class TestTaskResult(unittest.TestCase):
    def setUp(self):
        pass

    def test_init(self):
        m = TaskResult("mytask", "1.1.1", 111)
        self.assertIsNotNone(m)

    def test_missing_taskid(self):
        tr = None
        try:
            tr = TaskResult(None, "1.1.1", 111)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_missing_task_version(self):
        tr = None
        try:
            tr = TaskResult("mytask", None, 111)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_non_str_task_version(self):
        tr = None
        try:
            tr = TaskResult("mytask", 1.1, 111)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_missing_tmoid(self):
        tr = None
        try:
            tr = TaskResult("mytask", "1.1.1", None)
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_non_numeric_tmoid(self):
        tr = None
        try:
            tr = TaskResult("mytask", "1.1.1", "abc")
        except ValueError:
            assert(True)
        else:
            assert(False)
        self.assertIsNone(tr)

    def test_add(self):
        tr = TaskResult("mytask", "1.1.1", 38974823)
        tr.add("results", "Here are my results")
        self.assertEqual(tr.get_data("results"), "Here are my results")
        self.assertEqual(tr["results"], "Here are my results")

    def test_add_nested_data(self):
        tr = TaskResult("mytask", "1.1.1", 10098)
        tr.add("results", {"a": "Nested"})
        self.assertEqual(tr.get_data("results"), {"a": "Nested"})
        self.assertEqual(tr["results"], {"a": "Nested"})

    def test_missing_data(self):
        tr = TaskResult("mytask", "1.1.1", 10098)
        tr.add("results", {"a": "Nested"})
        self.assertIsNone(tr.get_data("nothere"))

    def test_missing_data_strict(self):
        tr = TaskResult("mytask", "1.1.1", 10098)
        tr.add("results", {"a": "Nested"})
        try:
            tr.get_data_strict("nothere")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_dict_loop(self):
        tr = TaskResult("mytask", "1.1.1", 8734)
        tr.add("a", "1")
        tr.add("b", "2")
        self.assertEqual(set(tr.keys()), set(["a", "b"]))

    def test_finalise_success(self):
        tr = TaskResult("mytask", "1.1.1", 123)
        tr.add("results", "result")
        tr.finish()
        self.assertEqual(tr.success, True)

    def test_finalise_failure(self):
        tr = TaskResult("mytask", "1.1.1", 123)
        tr.add("results", "result")
        tr.finish(err="Everything broken")
        self.assertFalse(tr.success)
        self.assertIsNotNone(tr.err)

    def test_timer_success(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish()
        self.assertIsNotNone(tr.time_end)
        self.assertLess(tr.time_start, tr.time_end)

    def test_timer_fail(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish(err="Everything broke")
        self.assertIsNotNone(tr.time_end)
        self.assertLess(tr.time_start, tr.time_end)
        self.assertEqual(tr[F.META][F.META_START_TIME], tr.time_start)
        self.assertEqual(tr[F.META][F.META_END_TIME], tr.time_end)

    def test_success(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish()
        self.assertTrue(tr.success)
        self.assertIsNone(tr.err)

    def test_failure(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish(err="Everything broke")
        self.assertFalse(tr.success)
        self.assertEqual(tr.err, "Everything broke")

    def test_msg(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish(msg="Diagnostic info")
        self.assertEqual(tr[F.META][F.META_MSG], "Diagnostic info")

    def test_reserved_name(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        try:
            tr.add(F.META, "Reserved field")
        except ValueError:
            assert(True)
        else:
            assert(False)

    def test_obj_json_import(self):
        tr = TaskResult("mytask", "1.1.1", 100)
        tr.add("whois", "My whois data")
        tr.finish(err="Everything broke")

        tr_json = json.dumps(tr)

        tr2 = TaskResult.init_from_dict("mytask", 100, json.loads(tr_json))
        self.assertEqual(tr2.get_data("whois"), "My whois data")
        self.assertFalse(tr2.success)
        self.assertEqual(tr2.err, "Everything broke")
        self.assertEqual(tr2.task_version, "1.1.1")
