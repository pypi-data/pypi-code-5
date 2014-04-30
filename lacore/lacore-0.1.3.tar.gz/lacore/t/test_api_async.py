from testtools import TestCase
from testtools.deferredruntest import AsynchronousDeferredRunTest
from testtools.deferredruntest import assert_fails_with
from mock import patch, Mock
from twisted.internet import defer
from lacore.exceptions import (ApiAuthException, ApiUnavailableException,
                               ApiErrorException)
from lacore.t.test_api import LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE
from itertools import imap
from . import makeprefs
import json


class ApiAsyncTest(TestCase):
    run_test_with = AsynchronousDeferredRunTest

    def _makeit(self, prefs={}):
        from lacore.api import RequestsFactory
        with patch('lacore.api.Api') as api:
            RequestsFactory(prefs)
            args, _ = api.call_args
            return args[1]

    @defer.inlineCallbacks
    def test_request_simple(self):
        session = self._makeit()
        for m in ['get', 'post', 'patch']:
            with patch('treq.' + m) as method:
                with patch('treq.content') as content:
                    content.return_value = "{}"
                    rsp = Mock(code=200)
                    url = self.getUniqueString()
                    method.return_value = defer.succeed(rsp)
                    r = yield getattr(session, m)(url)
                    self.assertEqual(r, {})
                    self.assertEqual((url,), method.call_args[0])

    @defer.inlineCallbacks
    def test_request_get_fail(self):
        session = self._makeit()
        with patch('treq.get') as get:
            with patch('treq.content') as content:
                content.return_value = "{}"
                phrase = self.getUniqueString()
                rsp = Mock(code=400, phrase=phrase)
                get.return_value = defer.succeed(rsp)
                url = self.getUniqueString()
                e = yield assert_fails_with(
                    session.get(url), ApiErrorException)
                self.assertEqual(ApiErrorException.msg, str(e))
                self.assertEqual('400 ' + phrase, e.exc)
                self.assertEqual((url,), get.call_args[0])

    @defer.inlineCallbacks
    def test_request_get_auth(self):
        auth = (self.getUniqueString(), self.getUniqueString())
        session = self._makeit(
            {'user': auth[0], 'pass': auth[1], 'verify': False})
        with patch('treq.get') as get:
            with patch('treq.content') as content:
                content.return_value = "{}"
                get.side_effect = [
                    defer.succeed(Mock(code=401)),
                    defer.succeed(Mock(code=200))]
                url = self.getUniqueString()
                r = yield session.get(url)
                self.assertEqual(r, {})
                self.assertIn('auth', get.call_args[1])
                self.assertEqual(auth, get.call_args[1]['auth'])

    @defer.inlineCallbacks
    def test_request_get_auth_fail(self):
        session = self._makeit()
        with patch('treq.get') as get:
            with patch('treq.content') as content:
                content.return_value = "{}"
                get.side_effect = [
                    defer.succeed(Mock(code=401)),
                    defer.succeed(Mock(code=401))]
                url = self.getUniqueString()
                e = yield assert_fails_with(
                    session.get(url), ApiAuthException)
                self.assertEqual(ApiAuthException.msg, str(e))
                self.assertEqual((url,), get.call_args[0])

    @defer.inlineCallbacks
    def test_request_get_404(self):
        session = self._makeit()
        with patch('treq.get') as get:
            with patch('treq.content') as content:
                content.return_value = "{}"
                rsp = Mock(code=404)
                get.return_value = defer.succeed(rsp)
                url = self.getUniqueString()
                e = yield assert_fails_with(
                    session.get(url),
                    ApiUnavailableException)
                self.assertEqual(ApiUnavailableException.msg, str(e))
                self.assertEqual((url,), get.call_args[0])

    def test_finalize(self):
        _gets = map(defer.succeed,
                    map(json.loads,
                        [LA_ENDPOINTS_RESPONSE, LA_CAPSULES_RESPONSE]))
        r = self.getUniqueString()
        _patches = imap(defer.succeed, [r])
        sargs = {'get.side_effect': _gets,
                 'patch.side_effect': _patches}
        s = Mock(**sargs)
        from lacore.api import Api
        api = Api(makeprefs()['api'], session=s)
        state = Mock(uri='foo', sandbox=False,
                     capsule={'resource_uri': '/1'})
        op = api.upload(Mock(title='',
                             description='',
                             meta=Mock(size=1)), state)
        d = op.finalize()
        d.addCallback(lambda x: self.assertEqual(r, x))
        d.addCallback(lambda x: self.assertEqual(
            s.patch.call_args[0], ('foo',)))
        d.addCallback(lambda x: self.assertEqual(
            json.loads(s.patch.call_args[1]['data']),
            {
                'status': 'uploaded',
                'parts': 0,
                'size': 1
            }))
        return d
