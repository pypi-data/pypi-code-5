#
# Copyright (c) 2008-2014 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Password

# import local packages

from ztfy.baseskin import _


#
# Skinning interfaces
#

class ISkinnable(Interface):
    """Base skinnable content interface

    This interface is used for any object managing a skin.
    An adapter is used during traversal t automatically
    apply selected skin.
    """

    def getSkin(self):
        """Get skin name matching current context"""


#
# Default view interfaces
#

class IDefaultView(Interface):
    """Interface used to get object's default view"""

    viewname = TextLine(title=_("View name"),
                        description=_("Name of the default view matching object, request and (optionally) current view"),
                        required=True,
                        default=u'@@index.html')

    def getAbsoluteURL(self):
        """Get full absolute URL of the default view"""


class IContainedDefaultView(IDefaultView):
    """Interface used to get object's default view while displayed inside a container"""


#
# Dialogs interfaces
#

class IDialog(Interface):
    """Base interface for AJAX dialogs"""

    dialog_class = Attribute(_("Default dialog CSS class"))

    resources = Attribute(_("List of resources needed by this dialog"))


class IDialogTitle(Interface):
    """Dialog title getter interface"""

    def getTitle(self):
        """Get dialog title"""


#
# Base front-office views
#

class IBaseViewlet(Interface):
    """Marker interface for base viewlets"""


class IBaseIndexView(Interface):
    """Marker interface for base index view"""


#
# Presentation management interfaces
#

class IBasePresentationInfo(Interface):
    """Base interface for presentation infos"""


class IPresentationForm(Interface):
    """Marker interface for default presentation edit form"""


class IPresentationTarget(Interface):
    """Interface used inside skin-related edit forms"""

    target_interface = Attribute(_("Presentation form target interface"))


#
# Login form attributes
#

class ILoginFormFields(Interface):
    """Login form fields interface"""

    username = TextLine(title=_("login-field", "Login"),
                        required=True)

    password = Password(title=_("password-field", "Password"),
                        required=True)

    came_from = TextLine(title=_("came-from", "Original address"),
                         required=False)
