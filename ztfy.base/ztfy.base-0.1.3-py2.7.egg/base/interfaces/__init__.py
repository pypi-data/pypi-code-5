### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Text, List

# import local packages
from ztfy.file.schema import ImageField

from ztfy.base import _


#
# Generic interface
#

class IUniqueID(Interface):
    """Interface for objects with unique ID"""

    oid = TextLine(title=_("Unique ID"),
                   description=_("Globally unique identifier of this content can be used to create internal links"),
                   readonly=True)


class IPathElements(Interface):
    """Interface used to index object's path"""

    paths = List(title=_("Path elements"),
                 description=_("List of path elements matching adapted object"),
                 value_type=TextLine())


#
# Content base interface
#

class IBaseContentType(Interface):
    """Base content type interface"""

    content_type = Attribute(_("Content type"))


class IBaseContent(IBaseContentType):
    """Base content interface"""

    title = TextLine(title=_("Title"),
                     description=_("Content title"),
                     required=True)

    shortname = TextLine(title=_("Short name"),
                         description=_("Short name of the content can be displayed by several templates"),
                         required=True)

    description = Text(title=_("Description"),
                       description=_("Internal description included in HTML 'meta' headers"),
                       required=False)

    keywords = TextLine(title=_("Keywords"),
                        description=_("A list of keywords matching content, separated by commas"),
                        required=False)

    header = ImageField(title=_("Header image"),
                        description=_("This banner can be displayed by skins on page headers"),
                        required=False)

    heading = Text(title=_("Heading"),
                   description=_("Short header description of the content"),
                   required=False)

    illustration = ImageField(title=_("Illustration"),
                              description=_("This illustration can be displayed by several presentation templates"),
                              required=False)

    illustration_title = TextLine(title=_("Illustration alternate title"),
                                  description=_("This text will be used as an alternate title for the illustration"),
                                  required=False)


class IMainContent(Interface):
    """Marker element for first level site contents"""


