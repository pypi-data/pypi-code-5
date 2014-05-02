# -*- coding: utf8 -*-

from zope.interface import Interface
from zope.interface import Attribute


class IJSDataProvider(Interface):
    """Generic interface for a callable object able to provide JavaScript configuration data"""

    context = Attribute("""The Plone context""")
    request = Attribute("""The Zope request""")
    view = Attribute("""The current view""")

    def __call__():
        """Provider output"""


class IJSONDataProvider(IJSDataProvider):
    """
    An object that provide JSON configuration data.
    It will be putted inside a script of type text/collective.jsconfiguration.xml
    """


class IJSObjectDataProvider(IJSDataProvider):
    """
    An object that provide native JavaScript configuration data.
    It will be putted inside a standard script of type text/javascript.
    
    This must be implemented with a named adapter
    """


class IDOMDataProvider(IJSDataProvider):
    """
    An object that provide configuration data through HTML 5 data attributes.
    It will be putted inside a script of type text/collective.jsconfiguration.xml
    """
