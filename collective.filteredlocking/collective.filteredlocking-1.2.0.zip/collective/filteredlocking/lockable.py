# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from collective.filteredlocking import config
from plone.locking.interfaces import STEALABLE_LOCK
from plone.locking.lockable import TTWLockable


class FilteredTTWLockable(TTWLockable):
    """An object that is being locked through-the-web
    """

    def stealable(self, lock_type=STEALABLE_LOCK):
        # Whatever is the lock permission settings, I can always remove my locks
        if self._lock_is_mine():
            return True
        # Checking the new permission
        if not self._user_can_unlock():
            return False
        return super(FilteredTTWLockable, self).stealable(lock_type)

    def _lock_is_mine(self):
        info = self.lock_info()
        userid = getSecurityManager().getUser().getId() or None
        for l in info:
            # The lock is in fact held by the current user
            if l['creator'] == userid:
                return True
        return False
    
    def _user_can_unlock(self):
        sm = getSecurityManager()
        return bool(sm.checkPermission(config.CanUnlockObjects, self.context))
