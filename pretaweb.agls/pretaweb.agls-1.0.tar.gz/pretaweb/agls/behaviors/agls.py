from AccessControl.SecurityManagement import getSecurityManager

from zope import schema
from zope.interface import alsoProvides

from z3c.form.interfaces import IEditForm, IAddForm
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.dexterity.behaviors.metadata import DCFieldProperty, \
    ICategorization, Categorization

from collective.z3cform.keywordwidget.field import Keywords
from collective.z3cform.keywordwidget.widget import KeywordFieldWidget

try:
    from z3c.form.browser.textlines import TextLinesFieldWidget
except ImportError:
    from plone.z3cform.textlines.textlines import TextLinesFieldWidget

from pretaweb.agls.form.widget import Z3CFormKeywordFieldWidget
from pretaweb.agls import messageFactory as _


# Behavior interface to display AGLS Metadata fields on Dexterity
# content edit forms.


AGLS_FIELDS = (
    'agls_title_override', 'agls_title',
    'agls_desc_override', 'agls_desc',
    'creation_date',
    'agls_author_override', 'agls_author',
    'agls_type_override', 'agls_type',
    'agls_id_override', 'agls_id',
    'agls_publisher_override', 'agls_publisher',
    'agls_format_override', 'agls_format'
)

class IAGLS(form.Schema):
    """Here we define new AGLS fieldset as well as extend and modify
    existing Categorization fielset:
    
      * add AGLSType field
      * set KeywordWidget to subjects field
    """
    
    # Categorization fieldset
    form.fieldset(
        'categorization',
        label=_(u'Categorization'),
        fields=['subjects', 'language', 'AGLSType'],
    )
    
    subjects = Keywords(
        title=_(u'label_categories', default=u'Categories'),
        description=_(u'help_categories', default=u"Also known as keywords, "
                      "tags or labels, these help you categorize your "
                      "content."),
        required=False,
        value_type=schema.TextLine(),
        missing_value=()
    )
    form.widget(subjects=Z3CFormKeywordFieldWidget)
    
    language = ICategorization['language']
    
    # Main AGLS Type
    AGLSType = schema.TextLine(
        title=_(u"AGLS Type"),
        description=_(u"Enter here text line to use in AGLS Type tag."),
        required=False,
        default=u'',
        missing_value=u''
    )
    
    
    # AGLS fieldset
    form.fieldset(
        'agls_metadata',
        label=_(u'Agls metadata'),
        fields=list(AGLS_FIELDS),
    )
    
    # AGLS Title
    agls_title_override = schema.Bool(
        title=_(u"Override AGLS Title"),
        description=_(u"By default object's title field is used."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_title = schema.TextLine(
        title=_(u"AGLS Title"),
        description=_(u"Enter here custom title to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )
    
    # AGLS Description
    agls_desc_override = schema.Bool(
        title=_(u"Override AGLS Description"),
        description=_(u"By default object's description field is used."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_desc = schema.Text(
        title=_(u"AGLS Description"),
        description=_(u"Enter here custom description to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )

    # AGLS Date
    creation_date = schema.Datetime(
        title=_(u"Creation Date"),
        description=_(u"Date this object was created. Used for AGLS Date meta "
                      "tag."),
        required=False
    )
    
    # AGLS Author
    agls_author_override = schema.Bool(
        title=_(u"Override AGLS Author"),
        description=_(u"By default object's creator field is used or global "
                      "control panel settings if configured."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_author = schema.TextLine(
        title=_(u"AGLS Author"),
        description=_(u"Enter here custom author to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )

    # AGLS Type
    agls_type_override = schema.Bool(
        title=_(u"Override AGLS Type"),
        description=_(u"By default object's AGLS Type, from Categorization tab,"
                      " field is used in AGLS tag."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_type = schema.TextLine(
        title=_(u"AGLS Type"),
        description=_(u"Enter here custom Type to use in AGLS Type Tag."),
        required=False,
        default=u'',
        missing_value=u''
    )

    # AGLS Identifier
    agls_id_override = schema.Bool(
        title=_(u"Override AGLS Identifier"),
        description=_(u"By default object's UID attribute is used for AGLS "
                      "tag."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_id = schema.TextLine(
        title=_(u"AGLS Identifier"),
        description=_(u"Enter here custom identifier to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )
    
    # AGLS Publisher
    agls_publisher_override = schema.Bool(
        title=_(u"Override AGLS Publisher"),
        description=_(u"By default object's creator field is used or global "
                      "control panel settings if configured."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_publisher = schema.TextLine(
        title=_(u"AGLS Publisher"),
        description=_(u"Enter here custom publisher to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )
    
    # AGLS Format
    agls_format_override = schema.Bool(
        title=_(u"Override AGLS Format"),
        description=_(u"By default object's content-type will be used. Either "
                      "html or file mime-type for File/Image based content "
                      "types."),
        required=False,
        default=False,
        missing_value=False
    )
    
    agls_format = schema.TextLine(
        title=_(u"AGLS Format"),
        description=_(u"Enter here custom format to use in AGLS tag."),
        required=False,
        default=u'',
        missing_value=u''
    )
    
    # display fields only on edit forms
    form.omitted('AGLSType', 'subjects', 'language', *AGLS_FIELDS)
    form.no_omit(IEditForm, 'AGLSType', 'subjects', 'language', *AGLS_FIELDS)
    form.no_omit(IAddForm, 'AGLSType', 'subjects', 'language', *AGLS_FIELDS)

# Mark this interface as form field provider
alsoProvides(IAGLS, IFormFieldProvider)

class AGLS(Categorization):

    agls_title_override = DCFieldProperty(IAGLS['agls_title_override'])
    agls_title = DCFieldProperty(IAGLS['agls_title'])
    agls_desc_override = DCFieldProperty(IAGLS['agls_desc_override'])
    agls_desc = DCFieldProperty(IAGLS['agls_desc'])
    creation_date = DCFieldProperty(IAGLS['creation_date'])
    agls_author_override = DCFieldProperty(IAGLS['agls_author_override'])
    agls_author = DCFieldProperty(IAGLS['agls_author'])
    agls_type_override = DCFieldProperty(IAGLS['agls_type_override'])
    agls_type = DCFieldProperty(IAGLS['agls_type'])
    agls_id_override = DCFieldProperty(IAGLS['agls_id_override'])
    agls_id = DCFieldProperty(IAGLS['agls_id'])
    agls_publisher_override = DCFieldProperty(IAGLS['agls_publisher_override'])
    agls_publisher = DCFieldProperty(IAGLS['agls_publisher'])
    agls_format_override = DCFieldProperty(IAGLS['agls_format_override'])
    agls_format = DCFieldProperty(IAGLS['agls_format'])
    AGLSType = DCFieldProperty(IAGLS['AGLSType'])
