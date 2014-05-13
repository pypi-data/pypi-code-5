from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('Keyword', 'CodeKeyword')
    ignored_relations = set(('descendant_of',))

    def to_test_etypes(self):
        # only test the cube related entities
        return set(('Classification', 'Keyword', 'CodeKeyword'))

    def list_startup_views(self):
        return ()

if __name__ == '__main__':
    unittest_main()
