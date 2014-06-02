
from Acquisition import aq_parent
from Acquisition import aq_inner

from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder

from Products.ATContentTypes.lib.constraintypes import getParent
from Products.ATContentTypes.lib.constraintypes import DISABLED, ENABLED, ACQUIRE

from logging import getLogger
logger = getLogger(__name__)
info = logger.info

def getImmediatelyAddableTypes(self, context=None):
    """Get the list of type ids which should be immediately addable.
    If enableTypeRestrictions is ENABLE, return the list set; if it is
    ACQUIRE, use the value from the parent; if it is DISABLE, return
    all type ids allowable on the item.
    """
    if context is None:
        context = self
    mode = self.getConstrainTypesMode()

    if mode == DISABLED:
        return [fti.getId() for fti in \
                    self.getDefaultAddableTypes(context)]
    elif mode == ENABLED:
        return self.getField('immediatelyAddableTypes').get(self)
    elif mode == ACQUIRE:
        parent = getParent(self)
        if not parent or parent.portal_type == 'Plone Site':
            return [fti.getId() for fti in \
                    PortalFolder.allowedContentTypes(self)]
        # Patch start
        # elif not parentPortalTypeEqual(self):
        #     default_allowed = [fti.getId() for fti in \
        #             PortalFolder.allowedContentTypes(self)]
        #     return [t for t in parent.getImmediatelyAddableTypes(context) \
        #                if t in default_allowed]
        # Patch end
        else:
            parent = aq_parent(aq_inner(self))
            return parent.getImmediatelyAddableTypes(context)
    else:
        raise ValueError, "Invalid value for enableAddRestriction"

def allowedContentTypes(self, context=None):
    """returns constrained allowed types as list of fti's
    """
    # import pdb;pdb.set_trace()
    if context is None:
        context = self
    mode = self.getConstrainTypesMode()

    # Short circuit if we are disabled or acquiring from non-compatible
    # parent

    parent = getParent(self)
    if mode == DISABLED or (mode == ACQUIRE and not parent):
        return PortalFolder.allowedContentTypes(self)
    # Patch start
    # elif mode == ACQUIRE and not parentPortalTypeEqual(self):
    #     globalTypes = self.getDefaultAddableTypes(context)
    #     if parent.portal_type == 'Plone Site':
    #         return globalTypes
    #     else:
    #         allowed = list(parent.getLocallyAllowedTypes(context))
    #         return [fti for fti in globalTypes if fti.getId() in allowed]
    # Patch end
    else:
        globalTypes = self.getDefaultAddableTypes(context)
        allowed = list(self.getLocallyAllowedTypes())
        ftis = [fti for fti in globalTypes if fti.getId() in allowed]
        return ftis

info('patched %s', 'Products.ATContentTypes.lib.constraintypes.ConstrainTypesMixin for Add menu')
