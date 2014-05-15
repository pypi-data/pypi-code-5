# -*- coding: utf-8 -*-

import unittest
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.locking.interfaces import IRefreshableLockable
from collective.filteredlocking.testing import FILTERED_LOCKING_INTEGRATION_TESTING


class BaseTestCase(unittest.TestCase):

    layer = FILTERED_LOCKING_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        login(portal, TEST_USER_NAME)
        portal.invokeFactory(type_name='Document', id="document", title="The doc")

    def test_editor_can_unlock(self):
        # Default Plone behavior: Editor can unlock other's people lock
        portal = self.layer['portal']
        login(portal, 'user1')
        lockable = IRefreshableLockable(portal.document)
        self.assertTrue(lockable._user_can_unlock())
        self.assertTrue(lockable.stealable())

    def test_can_remove_my_lock(self):
        portal = self.layer['portal']
        login(portal, 'user1')
        lockable = IRefreshableLockable(portal.document)
        lockable.lock()
        setRoles(portal, 'user1', ['Member', ])
        lockable = IRefreshableLockable(portal.document)
        # Not editor anymore...
        self.assertFalse(lockable._user_can_unlock())
        # ...but can unlock
        self.assertTrue(lockable._lock_is_mine())
        self.assertTrue(lockable.stealable())

        
