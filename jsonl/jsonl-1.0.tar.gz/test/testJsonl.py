import unittest
import jsonl
import json

class testJSONL(unittest.TestCase):

    def setUp(self):
        self.tv = '{"a":1}'
        self.tv1 = '{"a":{"b":2}, "c":3}'
        self.tv_ = {"a":1}
        self.tv1_ = {"a":{"b":2}, "c":3}
        self.tvn_ = {None:1}

    def tearDown(self):
        pass

    def testNone(self):
        a = jsonl.dumps(self.tvn_)
        r = jsonl.loads(a)
        assert r.null == 1

    def testSimpleAttribute(self):
        r = jsonl.loads(self.tv)
        assert r.a == 1

    def testComplexAttribute(self):
        r = jsonl.loads(self.tv1)
        assert r.a.b == 2
        assert r.c == 3

    def testLoadsImmutableNamedTuple(self):
        r = jsonl.loads(self.tv1, __mutable__=False)
        assert r.a.__class__.__name__ == jsonl.OBJECT_NAME
        for i in [r, r.a]:
            try:
                setattr(i, 'test', 1)
            except AttributeError:
                assert True
            else:
                assert False

    def testLoadsMutableObject(self):
        eV = 123
        r = jsonl.loads(self.tv1, __mutable__=True)
        assert r.a.__class__.__name__ == jsonl.OBJECT_NAME
        for i in [r, r.a]:
            try:
                setattr(i, 'test', eV)
            except Exception as _e:
                assert False
            else:
                assert r.test == eV

    def testLoadsMutableObjectByDefault(self):
        r = jsonl.loads(self.tv1)
        assert r.a.__class__.__name__ == jsonl.OBJECT_NAME

    def testDumps(self):
        rd = jsonl.dumps(self.tv_)
        r = jsonl.loads(rd)
        assert r.a == 1

    def testComplexDumps(self):
        rd = jsonl.dumps(self.tv1_)
        r = jsonl.loads(rd)
        assert r.a.__class__.__name__ == jsonl.OBJECT_NAME
        assert r.a.b == 2
        assert r.c == 3

    def testDumpsEquivelance(self):
        assert json.dumps(self.tv) == jsonl.dumps(self.tv)

    def testDumpsComplexEquivelance(self):
        assert json.dumps(self.tv1) == jsonl.dumps(self.tv1)

if __name__ == '__main__':
    unittest.main()

