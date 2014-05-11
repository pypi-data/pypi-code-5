#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IButton

# import local interfaces

# import Zope3 packages
from z3c.form.button import Button
from zope.interface import implements

# import local packages


class IResetButton(IButton):
    """Reset button interface"""


class ResetButton(Button):
    """Reset button"""

    implements(IResetButton)


class ICloseButton(IButton):
    """Close button interface"""


class CloseButton(Button):
    """Close button"""

    implements(ICloseButton)
