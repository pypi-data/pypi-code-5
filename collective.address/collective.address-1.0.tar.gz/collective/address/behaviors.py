from Products.CMFPlone.utils import safe_unicode
from collective.address import messageFactory as _
from collective.address.vocabulary import get_pycountry_name
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IAddress(model.Schema):
    """Address schema.
    """
    street = schema.TextLine(
        title=_(u'label_street', default=u'Street'),
        description=_(u'help_street', default=u''),
        required=False
    )
    zip_code = schema.TextLine(
        title=_(u'label_zip_code', default=u'Zip Code'),
        description=_(u'help_zip_code', default=u''),
        required=False
    )
    city = schema.TextLine(
        title=_(u'label_city', default=u'City'),
        description=_(u'help_city', default=u''),
        required=False
    )
    country = schema.Choice(
        title=_(u'label_country', default=u'Country'),
        description=_(u'help_country',
                      default=u'Select the country from the list.'),
        required=False,
        vocabulary='collective.address.CountryVocabulary'
    )


# Mark these interfaces as form field providers
alsoProvides(IAddress, IFormFieldProvider)


# Text indexing
@indexer(IAddress)
def searchable_text_indexer(obj):
    acc = IAddress(obj)
    text = ''
    text += '%s\n' % acc.street
    text += '%s\n' % acc.zip_code
    text += '%s\n' % acc.city
    text += '%s\n' % acc.country and get_pycountry_name(acc.country) or ''
    return safe_unicode(text.strip())
