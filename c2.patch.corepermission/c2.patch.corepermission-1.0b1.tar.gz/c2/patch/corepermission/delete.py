# coding: utf-8
# referenced to https://github.com/4teamwork/opengever.core/blob/master/opengever/base/monkeypatch.py

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from AccessControl.class_init import InitializeClass
from Products.Archetypes.BaseFolder import BaseFolderMixin

from logging import getLogger
logger = getLogger(__name__)
info = logger.info

def drop_protected_attr_from_ac_permissions(attribute, classobj):
    new_mappings = []
    for mapping in classobj.__ac_permissions__:
        perm, attrs = mapping
        if not attribute in attrs:
            new_mappings.append(mapping)
        else:
            modified_attrs = tuple([a for a in attrs if not a == attribute])
            modified_mapping = (perm, modified_attrs)
            new_mappings.append(modified_mapping)
    classobj.__ac_permissions__ = tuple(new_mappings)

drop_protected_attr_from_ac_permissions('manage_delObjects', BaseFolderMixin)
sec = ClassSecurityInfo()
sec.declareProtected(permissions.View,
                    'manage_delObjects')
sec.apply(BaseFolderMixin)
InitializeClass(BaseFolderMixin)

info('patched %s', 'Products.Archetypes.BaseFolder.BaseFolderMixin.manage_delObjects')

