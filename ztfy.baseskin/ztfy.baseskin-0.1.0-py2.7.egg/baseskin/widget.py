#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IFormLayer, IFieldWidget

# import local interfaces
from ztfy.baseskin.interfaces.form import IResetWidget, ICloseWidget
from ztfy.baseskin.schema import IResetButton, ICloseButton

# import Zope3 packages
from z3c.form.action import Action
from z3c.form.browser.submit import SubmitWidget
from z3c.form.button import ButtonAction
from z3c.form.widget import FieldWidget
from zope.component import adapter, adapts
from zope.interface import implementer, implementsOnly

# import local packages


#
# Reset button widget and action
#

class ResetWidget(SubmitWidget):
    """A reset button of a form."""

    implementsOnly(IResetWidget)

    klass = u'reset-widget'
    css = u'reset'


@adapter(IResetButton, IFormLayer)
@implementer(IFieldWidget)
def ResetFieldWidget(field, request):
    reset = FieldWidget(field, ResetWidget(request))
    reset.value = field.title
    return reset


class ResetButtonAction(ResetWidget, ButtonAction):
    """Reset button action"""

    adapts(IFormLayer, IResetButton)

    def __init__(self, request, field):
        Action.__init__(self, request, field.title)
        ResetWidget.__init__(self, request)
        self.field = field


#
# Close button widget and action
#

class CloseWidget(SubmitWidget):
    """A dialog close button"""

    implementsOnly(ICloseWidget)

    klass = u'close-widget'
    css = u'close'


@adapter(ICloseButton, IFormLayer)
@implementer(IFieldWidget)
def CloseFieldWidget(field, request):
    close = FieldWidget(field, CloseWidget(request))
    close.value = field.title
    return close


class CloseButtonAction(CloseWidget, ButtonAction):
    """Close button action"""

    adapts(IFormLayer, ICloseButton)

    def __init__(self, request, field):
        Action.__init__(self, request, field.title)
        CloseWidget.__init__(self, request)
        self.field = field
