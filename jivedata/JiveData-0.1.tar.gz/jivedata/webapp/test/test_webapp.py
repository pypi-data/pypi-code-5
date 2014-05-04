import unittest
from jivedata.webapp.jinja2_filters import (format_percentage,
                                            format_per_share_currency)


class Tester(unittest.TestCase):
    def test_format_percentage(self):
        raw = .128
        perc = format_percentage(raw)
        self.failUnless(perc == '12.8%')

        raw = '.074'
        perc = format_percentage(raw)
        self.failUnless(perc == '7.4%')

    def test_format_per_share_currency(self):
        raw = 12.8
        val = format_per_share_currency(raw)
        self.failUnless(val == '$12.80')

        raw = '18.78'
        val = format_per_share_currency(raw)
        self.failUnless(val == '$18.78')


if __name__ == '__main__':
    unittest.main()
