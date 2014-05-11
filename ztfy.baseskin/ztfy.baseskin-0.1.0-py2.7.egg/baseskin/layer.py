#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IFormLayer
from z3c.formui.interfaces import IFormUILayer
from z3c.jsonrpc.layer import IJSONRPCLayer
from z3c.layer.pagelet import IPageletBrowserLayer

# import local interfaces

# import Zope3 packages

# import local packages


class IBaseSkinLayer(IFormLayer, IFormUILayer, IPageletBrowserLayer, IJSONRPCLayer):
    """Base skin layer"""
