# -*- coding: utf8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.jsconfiguration.interfaces import IJSONDataProvider
from collective.jsconfiguration.interfaces import IDOMDataProvider
from collective.externalizelink.interfaces import IExternalizeLinkSettings
from collective.regjsonify.interfaces import IJSONifier
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implements


class ConfigurationReader(object):
    implements(IJSONDataProvider)
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    def __call__(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IExternalizeLinkSettings, check=False)
        return IJSONifier(settings).json()


class I18NReader(object):
    implements(IDOMDataProvider)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    __call__ = ViewPageTemplateFile('i18n.pt')
