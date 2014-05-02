# -*- coding: utf-8 -*-

import unittest
from collective.jsconfiguration.interfaces import IJSConfigurationLayer
from collective.jsconfiguration.interfaces import IDOMDataProvider
from collective.jsconfiguration.testing import JS_CONFIGURATION_INTEGRATION_TESTING
from collective.jsconfiguration.tests.base import BaseTestCase
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import provideAdapter
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces.browser import IHTTPRequest
from zope.publisher.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces import IATDocument


class DOMConfiguration(object):
    implements(IDOMDataProvider)

    template = ViewPageTemplateFile('test_dom.pt')
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        self.value1 = 'Hello'
        self.value2 = 'World'

    def __call__(self):
        return self.template()


class SpecialDOMConfiguration(DOMConfiguration):

    def __init__(self, context, request, view):
        super(SpecialDOMConfiguration, self).__init__(context, request, view)
        self.value2 = 'Plone'


class TestDOM(BaseTestCase):

    layer = JS_CONFIGURATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestDOM, self).setUp()
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Document', id='page', title="A Page",
                             text="<p>lorem ipsum</p>")
        provideAdapter(
                DOMConfiguration,
                (Interface,
                 IHTTPRequest,
                 Interface),
                provides=IDOMDataProvider,
                name=u'foo.dom.data'
            )


    def tearDown(self):
        super(TestDOM, self).tearDown()
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(DOMConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider,
                              name=u'foo.dom.data')
        gsm.unregisterAdapter(SpecialDOMConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider,
                              name=u'foo.dom.data')
        gsm.unregisterAdapter(DOMConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider,
                              name=u'bar.dom.data')
        gsm.unregisterAdapter(SpecialDOMConfiguration,
                              required=(IATDocument,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider,
                              name=u'foo.dom.data')
        gsm.unregisterAdapter(SpecialDOMConfiguration,
                              required=(IATDocument,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider,
                              name=u'bar.dom.data')
        gsm.unregisterAdapter(DOMConfiguration,
                              required=(IATDocument,
                                        IHTTPRequest,
                                        Interface),
                              provided=IDOMDataProvider)

    def test_configurtion_on_portal(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal())

    def test_configurtion_on_page(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal.page())

    def test_override(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialDOMConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IDOMDataProvider,
                name=u'foo.dom.data'
            )
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal())
        self.assertFalse("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal.page())
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>Plone</baz></foo>

</script>""" in portal.page())

    def test_multiple_registration(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialDOMConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IDOMDataProvider,
                name=u'bar.dom.data'
            )
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal.page())
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="bar.dom.data">

<foo><bar>Hello</bar><baz>Plone</baz></foo>

</script>""" in portal.page())

    def test_unnamed(self):
        portal = self.layer['portal']
        provideAdapter(
                DOMConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IDOMDataProvider,
            )
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml" id="foo.dom.data">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal.page())
        self.assertTrue("""<script type="text/collective.jsconfiguration.xml">

<foo><bar>Hello</bar><baz>World</baz></foo>

</script>""" in portal.page())
