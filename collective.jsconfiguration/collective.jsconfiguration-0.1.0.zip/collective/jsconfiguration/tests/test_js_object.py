# -*- coding: utf-8 -*-

import unittest
from collective.jsconfiguration.interfaces import IJSConfigurationLayer
from collective.jsconfiguration.interfaces import IJSObjectDataProvider
from collective.jsconfiguration.testing import JS_CONFIGURATION_INTEGRATION_TESTING
from collective.jsconfiguration.tests.base import BaseTestCase
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import provideAdapter
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces.browser import IHTTPRequest
from Products.ATContentTypes.interfaces import IATDocument


class JSObjectConfiguration(object):
    implements(IJSObjectDataProvider)
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        
    def __call__(self):
        return {'foo' : 'Hello World'}


class SpecialJSObjectConfiguration(JSObjectConfiguration):

    def __call__(self):
        return {'foo' : 'Hello Plone'}


class TestJSObject(BaseTestCase):

    layer = JS_CONFIGURATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestJSObject, self).setUp()
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Document', id='page', title="A Page",
                             text="<p>lorem ipsum</p>")
        provideAdapter(
                JSObjectConfiguration,
                (Interface,
                 IHTTPRequest,
                 Interface),
                provides=IJSObjectDataProvider,
                name=u'foo.bar'
            )

    def tearDown(self):
        super(TestJSObject, self).tearDown()
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(JSObjectConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              name=u'foo.bar')
        gsm.unregisterAdapter(SpecialJSObjectConfiguration,
                              required=(IATDocument,
                                        IHTTPRequest,
                                        Interface),
                              name=u'foo.bar')
        gsm.unregisterAdapter(JSObjectConfiguration,
                              required=(IATDocument,
                                        IHTTPRequest,
                                        Interface),
                              name=u'foo.bar.baz')
        gsm.unregisterAdapter(JSObjectConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              name=u'global_var')

    def test_configurtion_on_portal(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello World"};
</script>
""" in portal())

    def test_mono_name(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialJSObjectConfiguration,
                (Interface,
                 IHTTPRequest,
                 Interface),
                provides=IJSObjectDataProvider,
                name=u'global_var'
            )
        self.assertTrue("""<script type="text/javascript">

global_var = {"foo": "Hello Plone"};
</script>
""" in portal())

    def test_configurtion_on_page(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello World"};
</script>
""" in portal.page())

    def test_override(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialJSObjectConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IJSObjectDataProvider,
                name=u'foo.bar'
            )

        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello World"};
</script>
""" in portal())
        self.assertFalse("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello World"};
</script>
""" in portal.page())
        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello Plone"};
</script>
""" in portal.page())

    def test_multiple_registration(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialJSObjectConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IJSObjectDataProvider,
                name=u'foo.bar.baz'
            )
        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}

foo.bar = {"foo": "Hello World"};
</script>
""" in portal.page())
        self.assertTrue("""<script type="text/javascript">
if (typeof foo==='undefined') {
    foo = {};
}
if (typeof foo.bar==='undefined') {
    foo.bar = {};
}

foo.bar.baz = {"foo": "Hello Plone"};
</script>
""" in portal.page())
