import unittest
from jivedata.utils import truncator, format_aum


class Tester(unittest.TestCase):
    def test_truncator(self):
        raw = 'abcdefghijklmnopqrstuvwxyz'
        truncated = truncator(raw, 11)
        self.failUnless(len(truncated) == 11 + 3)

    def test_aum_formatter(self):
        thousands = '99000'
        million = '99000000'
        billion = '9900000000'

        self.failUnless(format_aum(thousands) == '$99.0M')
        self.failUnless(format_aum(million) == '$99.0B')
        self.failUnless(format_aum(billion) == '$9.9B')


if __name__ == '__main__':
    unittest.main()
