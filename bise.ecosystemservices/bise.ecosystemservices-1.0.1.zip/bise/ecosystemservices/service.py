from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.field import NamedFile
from plone.namedfile.field import NamedImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form import field
from z3c.form import group
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from bise.ecosystemservices import MessageFactory as _


# Interface class; used to define content-type schema.
class IService(form.Schema, IImageScaleTraversable):
    """
    Services
    """
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/service.xml to define the content type
    # and add directives here as necessary.
    section = schema.Choice(
        title = _(u'Section'),
        description = _(u'Section'),
        required=True,
        vocabulary = SimpleVocabulary([
            SimpleTerm(1, title=u"Provisioning"),
            SimpleTerm(2, title=u"Regulation and maintenance"),
            SimpleTerm(3, title=u"Cultural"),
        ])
        ) 
    division = schema.Choice(
        title = _(u'Division'),
        description = _(u'Division'),
        required=True,
        vocabulary = SimpleVocabulary([
            SimpleTerm(1, title=u"Nutrition"),
            SimpleTerm(2, title=u"Materials"),
            SimpleTerm(3, title=u"Energy"),
            SimpleTerm(4, title=u"Mediation of waste, toxics and other nuisances"),
            SimpleTerm(5, title=u"Mediation of flows"),
            SimpleTerm(6, title=u"Maintenance of physical, chemical, biological conditions"),
            SimpleTerm(7, title=u"Physical and experiential interactions"),
            SimpleTerm(8, title=u"Spiritual, symbolic and other interactions"),
        ])
        )     

    scale = schema.Choice(
        title = _(u'Scale level'),
        description = _(u'Scale level'),
        required=True,
        vocabulary = SimpleVocabulary([
            SimpleTerm(1, title=u"Global"),
            SimpleTerm(2, title=u"European"),
            SimpleTerm(3, title=u"National"),
            SimpleTerm(4, title=u"Subnational"),
        ]),
        default=2
        )  
    webmapid = schema.Text(
        title=_(u'Webmap ID'),
        description=_(u'Webmap id'),
        required=True,
        )            
    text = RichText(
        title=_(u'Description'),
        description=_(u'Description of the ecosystem service'),
        required=False,
        )



# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class Service(dexterity.Container):
    grok.implements(IService)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called serviceview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class ServiceView(grok.View):
    grok.context(IService)
    grok.require('zope2.View')
    grok.name('view')
