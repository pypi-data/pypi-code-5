# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class ExternalizeLinkLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.jsconfiguration
        xmlconfig.file('configure.zcml',
                       collective.externalizelink,
                       context=configurationContext)
        z2.installProduct(app, 'collective.externalizelink')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.externalizelink:default')
        #quickInstallProduct(portal, 'collective.externalizelink')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


EXTERNALIZE_LINK_FIXTURE = ExternalizeLinkLayer()
EXTERNALIZE_LINK_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(EXTERNALIZE_LINK_FIXTURE, ),
                       name="ExternalizeLink:Integration")
EXTERNALIZE_LINK_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(EXTERNALIZE_LINK_FIXTURE, ),
                       name="ExternalizeLink:Functional")
