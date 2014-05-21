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
class IStudy(form.Schema, IImageScaleTraversable):
    """
    Studies
    """
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/study.xml to define the content type
    # and add directives here as necessary.            
    text = RichText(
        title=_(u'Description'),
        description=_(u'Description of the ecosystem service'),
        required=False,
        )
    thumbnail = schema.Text(
        title=_(u'Study thumbnail'),
        description=_(u'Study thumbnail'),
        required=True,
        ) 
    document = schema.Text(
        title=_(u'Study document'),
        description=_(u'Study document'),
        required=True,
        ) 

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class Study(dexterity.Container):
    grok.implements(IStudy)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called studyview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class StudyView(grok.View):
    grok.context(IStudy)
    grok.require('zope2.View')
    grok.name('view')
