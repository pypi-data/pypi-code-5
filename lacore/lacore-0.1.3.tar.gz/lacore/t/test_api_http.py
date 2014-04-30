from testtools import TestCase
from mock import patch, Mock
from . import makeprefs


class ApiHttpTest(TestCase):
    def setUp(self):
        super(ApiHttpTest, self).setUp()
        self.prefs = makeprefs()['api']

    def _makeit(self):
        from lacore.api import RequestsFactory
        return RequestsFactory

    @patch('lacore.api.Api')
    def test_request_factory_no_prefs(self, api):
        factory = self._makeit()
        s = self.getUniqueString()
        self.patch(factory, 'TwistedRequestsSession',
                   Mock(return_value=s))
        factory()
        api.assert_called_with({}, s)

    @patch('lacore.api.Api')
    def test_request_factory(self, api):
        factory = self._makeit()
        s = self.getUniqueString()
        self.patch(factory, 'TwistedRequestsSession',
                   Mock(return_value=s))
        p = {self.getUniqueString(): self.getUniqueString()}
        factory(prefs=p)
        api.assert_called_with(p, s)

    @patch('lacore.api.Api')
    def test_request_factory_session(self, api):
        factory = self._makeit()
        factory()
        args, _ = api.call_args
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0], {})
        self.assertTrue(hasattr(args[1], 'get'))
        self.assertTrue(hasattr(args[1], 'post'))
        self.assertTrue(hasattr(args[1], 'patch'))
