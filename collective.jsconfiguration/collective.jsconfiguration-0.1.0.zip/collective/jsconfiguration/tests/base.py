# -*- coding: utf-8 -*-

import unittest

from zope import interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from collective.jsconfiguration.interfaces import IJSConfigurationLayer

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.markRequestWithLayer()
    
    def markRequestWithLayer(self):
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        request = self.layer['request']
        interface.alsoProvides(request, IJSConfigurationLayer)
    
