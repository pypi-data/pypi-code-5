import unittest
from model1 import *

class TestFilter(unittest.TestCase):
    def setUp(self):
        rollback()
        db_session.__enter__()
    def tearDown(self):
        rollback()
        db_session.__exit__()
    def test_filter_1(self):
        q = select(s for s in Student)
        result = set(q.filter(scholarship=0))
        self.assertEqual(result, set([Student[101], Student[103]]))
    def test_filter_2(self):
        q = select(s for s in Student)
        q2 = q.filter(scholarship=500)
        result = set(q2.filter(group=Group['3132']))
        self.assertEqual(result, set([Student[104]]))
    def test_filter_3(self):
        sql_debug(True)
        q = select(s for s in Student)
        q2 = q.filter(lambda s: s.scholarship > 500)
        result = set(q2.filter(lambda s: count(s.marks) > 0))
        self.assertEqual(result, set([Student[102], Student[105]]))
    def test_filter_4(self):
        sql_debug(True)
        q = select(s for s in Student)
        #q2 = q.filter(lambda s: s.scholarship > 500)
        #q3 = q2.order_by(1)
        result = set(q.filter(lambda s: count(s.marks) > 2))
        self.assertEqual(result, set([Student[102], Student[105]]))
