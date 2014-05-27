import os

from unittest.util import safe_repr

from .utils import compare_xml


class PostNLTestMixin(object):
    """ Mixin supplying XML equality test, backported from Django > 1.5. """

    def assertXMLEqual(self, xml1, xml2, msg=None):
        """
        Asserts that two XML snippets are semantically the same.
        Whitespace in most cases is ignored, and attribute ordering is not
        significant. The passed-in arguments must be valid XML.
        """
        try:
            result = compare_xml(xml1, xml2)
        except Exception as e:
            standardMsg = 'First or second argument is not valid XML\n%s' % e
            self.fail(self._formatMessage(msg, standardMsg))
        else:
            if not result:
                standardMsg = '%s != %s' % (
                    safe_repr(xml1, True), safe_repr(xml2, True)
                )
                self.fail(self._formatMessage(msg, standardMsg))

    def read_file(self, filename):
        """ Read file from data directory and return contents. """

        assert filename

        data_directory = os.path.join(os.path.dirname(__file__), 'data')

        f = open(os.path.join(data_directory, filename))

        return f.read()
