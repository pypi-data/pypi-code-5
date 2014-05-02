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


class JSConfigurationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.jsconfiguration
        xmlconfig.file('configure.zcml',
                       collective.jsconfiguration,
                       context=configurationContext)
        z2.installProduct(app, 'collective.jsconfiguration')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.jsconfiguration:default')
        #quickInstallProduct(portal, 'collective.jsconfiguration')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


JS_CONFIGURATION_FIXTURE = JSConfigurationLayer()
JS_CONFIGURATION_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(JS_CONFIGURATION_FIXTURE, ),
                       name="JSConfiguration:Integration")
JS_CONFIGURATION_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(JS_CONFIGURATION_FIXTURE, ),
                       name="JSConfiguration:Functional")
