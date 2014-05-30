from plone.theme.interfaces import IDefaultPloneLayer
import zope.interface

class IPackageLayer(IDefaultPloneLayer):
    """A layer specific to pretaweb.agls package"""


class IAGLSView(zope.interface.Interface):

    def Title():
        "@return agls override of Title or None"

    def Description():
        "@return agls override of Description or None"

    def Created():
        "@return ISO8601 of creation_date"

    def Creator():
        "@return agls override of author or None"

    def Subject():
        "@return agls override of Subject or None"

    def Type():
        "@return agls tyoe"

    def Identifier():
        "@return agls identifier or UUID"

    def Publisher():
        "@return agls publisher or None"

    def Format():
        "@return agls format override"
