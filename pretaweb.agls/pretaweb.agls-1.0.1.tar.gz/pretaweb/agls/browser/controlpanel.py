from zope import schema
from zope.interface import Interface

from Products.Five.browser import BrowserView

from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.z3cform import layout

from pretaweb.agls import messageFactory as _


class IAGLSSchema(Interface):
    """Global AGLS Settings"""
    
    default_author = schema.TextLine(
        title=_(u"Default AGLS Author"),
        description=_(u"If set, it's used for all content objects, unless "
                      "overriden on per object bases."),
        required=False,
        default=u'')
    
    default_publisher = schema.TextLine(
        title=_(u"Default AGLS Publisher"),
        description=_(u"If set, it's used for all content objects, unless "
                      "overriden on per object bases."),
        required=False,
        default=u'')

class AGLSControlPanelForm(RegistryEditForm):
    schema = IAGLSSchema

AGLSControlPanelView = layout.wrap_form(AGLSControlPanelForm,
    ControlPanelFormWrapper)
AGLSControlPanelView.label = u"AGLS Settings"
