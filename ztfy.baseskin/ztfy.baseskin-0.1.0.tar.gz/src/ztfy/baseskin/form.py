#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent

# import local packages
from ztfy.baseskin.interfaces.form import IFormObjectCreatedEvent, IFormObjectModifiedEvent


class FormObjectCreatedEvent(ObjectCreatedEvent):
    """Form object created event"""

    implements(IFormObjectCreatedEvent)

    def __init__(self, object, view):
        self.object = object
        self.view = view


class FormObjectModifiedEvent(ObjectModifiedEvent):
    """Form object modified event"""

    implements(IFormObjectModifiedEvent)

    def __init__(self, object, view, *descriptions):
        ObjectModifiedEvent.__init__(self, object, *descriptions)
        self.view = view
