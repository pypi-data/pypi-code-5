# -*- coding: utf8 -*-

from collective.externalizelink import _
from collective.regjsonify.fields import Base as JSONifyBase
from plone.registry.field import PersistentField
from z3c.form.object import registerFactoryAdapter
from zope import schema
from zope.interface import implements
from zope.interface import Interface


class IAdditionalAttrs(Interface):
    name = schema.TextLine(title=_(u"Attribute name"), required=True)
    value = schema.TextLine(title=_(u"Attribute value"), required=True)


class AdditionalAttrs(object):
    implements(IAdditionalAttrs)

    def __init__(self):
        self.name = None
        self.value = None


class IPersistentObject(Interface):
    pass

class PersistentObject(PersistentField, schema.Object):
    implements(IPersistentObject)


registerFactoryAdapter(IAdditionalAttrs, AdditionalAttrs)


class JSON(JSONifyBase):
    """Return the content of IAdditionalAttrs as a dict"""
    
    def data(self, record):
        return {'name': record.name, 'value': record.value}
