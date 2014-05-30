import unittest

import jsonl
import simplejson as json

class testJSONL(unittest.TestCase):
    def setUp(self):
        self.tv = '{"a":1}'
        self.tv1 = '{"a":{"b":2}, "c":3}'
        self.tv_ = {"count":1}
        self.tv1_ = {"a":{"b":2}, "c":[3]}
        self.tvn_ = {'null':1}
        self.tvn1_ = {None:1}
        self.tv2 = {None:1, True:False, 'a':[{'b':'bb', 'c':[1, {'f':'ff', 't':33}]}]}

    def tearDown(self):
        pass

    def testDumpMutableLoad1(self, tv=None):
        tv = tv or self.tv2
        a = jsonl.dumps(tv)
        b = jsonl.loads(a, __mutable__=True)
        c = jsonl.dumps(b)
        assert jsonl.isEqual(json.loads(a), json.loads(c))

    def testDumpImmutableLoad1(self, tv=None):
        tv = tv or self.tv2
        a = jsonl.dumps(tv)
        b = jsonl.loads(a, __mutable__=False)
        c = jsonl.dumps(b)
        assert jsonl.isEqual(json.loads(a), json.loads(c))

    def testCompare(self, tv=None):
        tv = tv or self.tv2
        a = jsonl.dumps(tv)
        for m in [True, False]:
            b = jsonl.loads(a, __mutable__=m)
            d = jsonl.loads(a, __mutable__=m)
            c = jsonl.dumps(b)
            assert jsonl.isEqual(json.loads(a), json.loads(c))
            assert jsonl.isEqual(a, c)
            assert jsonl.isEqual(b, d)
            assert jsonl.isEqual(c, d)

    def testNull(self):
        self.testNone(self.tvn1_)

    def testNone(self, tv=None):
        if tv == None:
            tv = self.tvn1_
        a = jsonl.dumps(tv)
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
        assert r.count == 1

    def testComplexDumps(self):
        rd = jsonl.dumps(self.tv1_)
        r = jsonl.loads(rd)
        assert r.a.__class__.__name__ == jsonl.OBJECT_NAME
        assert r.a.b == 2
        assert r.c == [3]

    def testDumpsEquivelance(self):
        a = json.dumps(self.tv)
        b = jsonl.dumps(self.tv)
        assert a == b

    def testDumpsComplexEquivelance(self):
        assert json.dumps(self.tv1) == jsonl.dumps(self.tv1)

    def testDumpMutableLoad(self, tv=None):
        tv = tv or self.tv
        a = jsonl.dumps(tv)
        b = jsonl.loads(a, __mutable__=True)
        c = jsonl.dumps(b)
        assert a == c

    def testDumpImmutableLoad(self, tv=None):
        tv = tv or self.tv
        a = jsonl.dumps(tv)
        b = jsonl.loads(a, __mutable__=True)
        c = jsonl.dumps(b)
        assert a == c

    def testDumpMutableLoadComplex(self):
        return self.testDumpMutableLoad(tv=self.tv1_)

    def testDumpImmutableLoadComplex(self):
        return self.testDumpImmutableLoad(tv=self.tv1_)

    def testWebEx1(self):
        FN = 'firstName'
        FNV = 'John'
        LN = 'lastName'
        LNV = 'Smith'
        voo = '''{
     "%s": "%s",
     "%s": "%s",
     "age": 25,
     "ageAtBirth": "0",
     "address":
     {
         "streetAddress": "21 2nd Street",
         "city": "New York",
         "state": "NY",
         "postalCode": "10021"
     },
     "phoneNumber":
     [
         {
           "type": "home",
           "number": "212 555-1234"
         },
         {
           "type": "fax",
           "number": "646 555-4567"
         }
     ]
     }''' % (FN, FNV, LN, LNV)
        def check(o):
            assert o.firstName == FNV
            assert o.lastName == LNV
            assert o.age == 25
            assert o.ageAtBirth == "0"
            assert o.address.streetAddress == "21 2nd Street"
            assert o.address.city == "New York"
            assert o.address.state == "NY"
            assert o.address.postalCode == "10021"
            assert o.phoneNumber[0].type == "home"
            assert o.phoneNumber[0].number == "212 555-1234"
            assert o.phoneNumber[1].type == "fax"
            assert o.phoneNumber[1].number == "646 555-4567"
        for m in [True, False]:
            l = jsonl.loads(voo, __mutable__=m)
            check(l)
            d = jsonl.dumps(l)
            assert jsonl.isEqual(l, d)
            for n in [True, False]:
                assert jsonl.isEqual(l, jsonl.loads(d, __mutable__=n))
                assert jsonl.isEqual(d, jsonl.loads(d, __mutable__=n))

if __name__ == '__main__':
    unittest.main()

