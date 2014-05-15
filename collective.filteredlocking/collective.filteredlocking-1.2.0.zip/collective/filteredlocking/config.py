# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo("collective.filteredlocking")

PROJECTNAME = 'collective.filteredlocking'

# Permission to unlock locked objects
# WARNING: this way the editor will inherit the permission on Plone site but the check will
# not be visibile. This is the only way to not force this product to have a GS profile 
security.declarePublic("CanUnlockObjects")
CanUnlockObjects = "collective.filteredlocking: Can unlock objects"
setDefaultRoles(CanUnlockObjects, ('Manager', 'Owner', 'Editor', 'Site Administrator'))
