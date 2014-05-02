# -*- coding: utf8 -*-

from collective.externalizelink import _
from zope.interface import Interface
from zope import schema
from .persistent_field import IAdditionalAttrs
from .persistent_field import PersistentObject


class IExternalizeLinkLayer(Interface):
    """Marker interface for collective.externalizelink product layer"""


class IExternalizeLinkSettings(Interface):
    """Control panel settings for collective.externalizelink"""

    enabled = schema.Bool(
            title=_(u"Enabled"),
            description=_(u"Uncheck to disable the popups handling"),
            required=False,
            default=True,
    )

    links_selection = schema.Tuple(
            title=_(u"Links selectors"),
            description=_('links_selection_help',
                          default=u"jQuery selectors that identify links to be externalized.\n"
                                  u"Inside selectors you can use the $PORTAL_URL marker that "
                                  u"will be replaced with the site URL."),
            required=False,
            default=('#region-content,#content a[href^="http"]:not(.link-plain):not([href^="$PORTAL_URL"])', ),
            missing_value=(),
            value_type=schema.TextLine(),
    )

    additional_attrs = schema.Tuple(
            title=_(u"Mark processed links"),
            description=_('help_additional_attrs',
                          default=u'Add additional attributes to links that will be marked as external.\n'
                                  u'If the attribute is already present the value will be added to the '
                                  u'existing attribute.'),
            value_type=PersistentObject(IAdditionalAttrs, title=_(u"Additional attribute")),
            required=False,
            default=(),
            missing_value=(),
    )
