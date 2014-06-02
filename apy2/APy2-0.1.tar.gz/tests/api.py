import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from apy2.core.api import Api


class TestApi(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.api = Api()

    def test_add1(self):
        @self.api.add()
        def foo():
            pass
        self.assertIsNotNone(self.api.get_function("foo"))

    def test_add_twice(self):
        @self.api.add()
        @self.api.add()
        def foo():
            pass
        foos = self.api.find_functions()
        self.assertEqual(1, len(foos))

    def test_add_twice_changed(self):
        @self.api.add("foo1")
        @self.api.add("bar3")
        def foo():
            pass
        foos = self.api.find_functions()
        self.assertEqual(2, len(foos))

    def test_get_none(self):
        a = self.api.get_function("foo")
        self.assertIsNone(a)
        @self.api.add()
        def foo1():
            pass
        a = self.api.get_function("foo")
        self.assertIsNone(a)

    def test_find1(self):
        @self.api.add()
        def foo1():
            pass

        @self.api.add()
        def foo2():
            pass

        f = self.api.find_functions("foo2")
        self.assertEqual(1, len(f))
        self.assertEqual("foo2", f[0].name)

    def test_find_all(self):
        many = 10
        for n in range(many):
            @self.api.add(name=("foo%s" % n))
            def foo():
                pass
        f = self.api.find_functions("*")
        self.assertEqual(many, len(f))
        self.assertEqual(f, self.api.find_functions())

    def test_context_root(self):
        @self.api.add()
        def foo1():
            pass
        c = self.api.context()
        self.assertEqual("foo1", c.foo1.name)
        self.assertEqual(c, self.api.context("root"))
        self.assertEqual(self.api.get_function("foo1").context, "root")

    def prepare_api(self):
        @self.api.add()
        def buy1():
            pass
        with self.api.context("supermarket"):
            @self.api.add()
            def buy1():
                pass
        with self.api.context("drugstore"):
            @self.api.add()
            def buy2():
                pass

    def test_context_add_with(self):
        self.prepare_api()

        al = self.api.find_functions(context="*")
        self.assertEqual(3, len(al))

        sm = self.api.find_functions(context="supermarket")
        self.assertEqual(1, len(sm))

    def test_context_add(self):
        @self.api.add()
        def buy2():
            pass
        self.api.enter_context("drugstore")
        @self.api.add()
        def buy2():
            pass
        self.api.exit_context()
        self.api.enter_context("supermarket")
        @self.api.add()
        def buy1():
            pass
        self.api.exit_context()

        al = self.api.find_functions(context="*")
        self.assertEqual(3, len(al))

        sm = self.api.find_functions(context="drugstore")
        self.assertEqual(1, len(sm))

    def test_context_with(self):
        self.prepare_api()

        buy1 = self.api.get_function("buy1", "supermarket")
        with self.api.context("supermarket") as c:
            self.assertEqual(buy1, c.buy1)

        buy2 = self.api.get_function("buy2", "drugstore")
        with self.api.context("drugstore") as c:
            self.assertEqual(buy2, c.buy2)

    def test_call_foo(self):
        @self.api.add()
        def foo():
            return 42

        f = self.api.get_function("foo")
        self.assertEqual(f(), 42)

    def test_aesthetic(self):
        self.prepare_api()
        b1 = self.api.get_function("buy1")
        self.assertEqual("<root.buy1()>", repr(b1))
        with self.api.context("drugstore") as c:
            self.assertEqual("<drugstore.buy2()>", repr(c.buy2))

    def test_bad_add(self):
        with self.assertRaises(Exception):
            @self.api.add()
            class A():
                pass

    def test_add_resource(self):
        self.skipTest("not yet")

    def test_foo_param(self):
        @self.api.add()
        def foo(a, b):
            return a + b

        f = self.api.get_function("foo")
        self.assertEqual(28, f(16, 12))

    def test_foo_opt_param(self):
        @self.api.add()
        def foo(a, b=10):
            return a + b

        f = self.api.get_function("foo")
        self.assertEqual(19, f(9))

    def test_foo_annotations(self):
        @self.api.add()
        def foo(a: int, b: str):
            return "%s-%s" % (b, a)

        f = self.api.get_function("foo")
        self.assertEqual("az-32", f(32, "az"))
        with self.assertRaises(Exception):
            f(32, 23)

    def test_foo_annotations2(self):
        @self.api.add()
        def f(a: int, b: str = "B", c: int=90):
            pass

        f(32, "bb", 0)
        with self.assertRaises(Exception):
            f(32, c="bb", b=0)

    def test_foo_get_args(self):
        @self.api.add()
        def foo(a, b, q, r):
            pass

        args = foo.get_args()
        self.assertEqual(args, ['a', 'b', 'q', 'r'])

    def test_aesthetic2(self):
        @self.api.add()
        def foo(a: int, b: str="egg", c="ham"):
            pass
        self.assertEqual(repr(foo),
                         "<root.foo(a: int, b: str='egg', c='ham')>")

    def test_foo_doc(self):
        @self.api.add()
        def foo(a, b):
            """this is the doc"""
            pass
        self.assertEqual(foo.doc, "this is the doc")

    def test_nested_context(self):
        with self.api.context("A"):
            @self.api.add()
            def foo():
                pass
            with self.api.context("B"):
                f = self.api.find_functions()
                self.assertEqual(0, len(f))
            f = self.api.find_functions()
            self.assertEqual(1, len(f))

    def test_eq_context(self):
        a = self.api.context("A")
        b = self.api.context("B")
        c = self.api.context("B")
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, "watermelon")
        self.assertEqual(b, c)

    def test_aesthetic3(self):

        @self.api.add(name="bar", context="spam")
        def foo():
            pass

        c = self.api.context("spam")
        self.assertEqual(repr(c),
                         "{context: 'spam', functions: ["
                         "<spam.bar()>]}")


if __name__ == '__main__':
    unittest.main()
