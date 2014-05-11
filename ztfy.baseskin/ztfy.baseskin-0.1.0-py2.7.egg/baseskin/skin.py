### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages

# import Zope3 interfaces
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserSkinType
from zope.traversing.interfaces import IBeforeTraverseEvent

# import local interfaces
from ztfy.baseskin.interfaces import ISkinnable

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.publisher.skinnable import applySkin

# import local packages


@adapter(ISkinnable, IBeforeTraverseEvent)
def handleSkinTraversal(object, event):
    if IBrowserRequest.providedBy(event.request):
        path = event.request.get('PATH_INFO', '')
        if '++skin++' not in path:
            skin_name = ISkinnable(object).getSkin()
            if not skin_name:
                skin_name = 'ZMI'
            skin = queryUtility(IBrowserSkinType, skin_name)
            if skin is not None:
                applySkin(event.request, skin)
