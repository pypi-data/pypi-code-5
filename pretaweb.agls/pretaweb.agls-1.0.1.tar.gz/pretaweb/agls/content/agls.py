from zope.component import adapts
from zope.interface import implements

from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes import public as atapi

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender, \
    ISchemaExtender, ISchemaModifier
from Products.Archetypes.atapi import DisplayList

from pretaweb.agls.browser.interfaces import IPackageLayer
from pretaweb.agls import messageFactory as _

# extender AT fields
class ExtensionBooleanField(ExtensionField, atapi.BooleanField):
    """Retrofitted boolean field"""

class ExtensionStringField(ExtensionField, atapi.StringField):
    """Retrofitted string field"""

class ExtensionTextField(ExtensionField, atapi.TextField):
    """Retrofitted text field"""

class ExtensionLinesField(ExtensionField, atapi.LinesField):
    """Retrofitted lines field"""

# Static for now. Will use ATVocabularyManager later

AGLS_TYPES = """
Audio
Booklet
Brochure
Case study
Checklist
Directive
Fact sheet
Form
Guidance/guideline
How to
Image/photo
Legislation
Manual
Minutes
News article
Plan
Policy
Presentation
Procedure
Publication
Report
Research
Standard
Strategy
Template
Terms of reference
Video
Websites
Work instruction
Survey
"""

#TODO needs to go in behaviour too
AGLS_TYPES_VOCAB = DisplayList([(v,v) for v in AGLS_TYPES.split('\n') if v.strip()]+[('','')])




class AGLSModifier(object):
    """Here we update creation date field to display it under AGLS tab"""

    adapts(IBaseContent)
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    
    layer = IPackageLayer
    
    def __init__(self, context):
        self.context = context
        
    def fiddle(self, schema):
        if schema.get('creation_date', None) is None:
            return

        for f in self.getFields():
            schema.addField(f)

        # move to AGLS schemata
        schema['creation_date'].schemata = 'AGLS Overrides'
        
        # update description
        schema['creation_date'].widget.description = _(u"Date this "
            "object was created. Used for AGLS Date meta tag.")
            
        # unhide it
        schema['creation_date'].widget.visible = {'edit': 'visible',
            'view': 'invisible'}
        
        # set starting year
        schema['creation_date'].widget.starting_year = 1990
        
        # move after AGLS description field
        schema.moveField('creation_date', after='agls_desc')

    """Adds AGLS fields to all archetypes objects that are used to override
    AGLA meta tags on a page on per object bases.
    """
    
    
    fields = [
        # AGLS Title
        ExtensionBooleanField("agls_title_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Title"),
                description=_(u"By default object's title field is used.")
            ),
            required=False,
            default=False
        ),
        ExtensionStringField("agls_title",
            schemata="AGLS Overrides",
            widget=atapi.StringWidget(
                label=_(u"AGLS Title"),
                description=_(u"Enter here custom title to use in AGLS tag.")
            ),
            required=False,
            default=''
        ),
        
        # AGLS Description
        ExtensionBooleanField("agls_desc_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Description"),
                description=_(u"By default object's description field is used.")
            ),
            required=False,
            default=False
        ),
        ExtensionTextField("agls_desc",
            schemata="AGLS Overrides",
            default_content_type='text/plain',
            allowable_content_types=('text/plain',),
            widget=atapi.TextAreaWidget(
                label=_(u"AGLS Description"),
                description=_(u"Enter here custom description to use in AGLS "
                              "tag.")
            ),
            required=False,
            default=''
        ),
        
        # AGLS Author
        ExtensionBooleanField("agls_author_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Author"),
                description=_(u"By default object's creator field is used or "
                              "global control panel settings if configured.")
            ),
            required=False,
            default=False
        ),
        ExtensionStringField("agls_author",
            schemata="AGLS Overrides",
            widget=atapi.StringWidget(
                label=_(u"AGLS Author"),
                description=_(u"Enter here custom author to use in AGLS tag.")
            ),
            required=False,
            default=''
        ),
        
        ExtensionStringField("AGLSType",
            schemata="categorization",
            widget=atapi.SelectionWidget(
                label=_(u"AGLS Type"),
                description=_(u"Enter here text line to use in AGLS Type tag.")
            ),
            required=False,
            default='',
            vocabulary=AGLS_TYPES_VOCAB


        ),
        
        # AGLS Identifier
        ExtensionBooleanField("agls_id_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Identifier"),
                description=_(u"By default object's UID attribute is used for "
                              "AGLS tag.")
            ),
            required=False,
            default=False
        ),
        ExtensionStringField("agls_id",
            schemata="AGLS Overrides",
            widget=atapi.StringWidget(
                label=_(u"AGLS Identifier"),
                description=_(u"Enter here custom identifier to use in AGLS "
                              "tag.")
            ),
            required=False,
            default=''
        ),
        
        # AGLS Publisher
        ExtensionBooleanField("agls_publisher_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Publisher"),
                description=_(u"By default object's creator field is used or "
                              "global control panel settings if configured.")
            ),
            required=False,
            default=False
        ),
        ExtensionStringField("agls_publisher",
            schemata="AGLS Overrides",
            widget=atapi.StringWidget(
                label=_(u"AGLS Publisher"),
                description=_(u"Enter here custom publisher to use in AGLS "
                              "tag.")
            ),
            required=False,
            default=''
        ),
        
        # AGLS Format
        ExtensionBooleanField("agls_format_override",
            schemata="AGLS Overrides",
            widget=atapi.BooleanWidget(
                label=_(u"Override AGLS Format"),
                description=_(u"By default object's content-type will be used. "
                              "Either html or file mime-type for File/Image "
                              "based content types.")
            ),
            required=False,
            default=False
        ),
        ExtensionStringField("agls_format",
            schemata="AGLS Overrides",
            widget=atapi.StringWidget(
                label=_(u"AGLS Format"),
                description=_(u"Enter here custom format to use in AGLS "
                              "tag.")
            ),
            required=False
        ),
        
    ]

    
    def getFields(self):
        """Return list of new fields we contribute to content"""
        return self.fields
