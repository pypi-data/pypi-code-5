"""template automatic tests

:organization: Logilab
:copyright: 2001-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from cubicweb.devtools import testlib


class DefaultTC(testlib.CubicWebTC):
    def test_something(self):
        req = self.request()
        rset = req.execute('Any X WHERE X is CodeKeyword')
        self.assert_(len(rset) > 0)

## uncomment the import if you want to activate automatic test for your
## template

# class AutoTest(testlib.AutomaticWebTest):
#     pass

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
