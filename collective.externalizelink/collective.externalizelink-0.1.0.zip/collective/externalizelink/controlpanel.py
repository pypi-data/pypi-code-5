# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.externalizelink import _
from collective.externalizelink.interfaces import IExternalizeLinkSettings
from plone.app.registry.browser import controlpanel
from plone.memoize.view import memoize
from z3c.form import button
from z3c.form import field
from z3c.form import group
from zope.component import getMultiAdapter


class ExternalizeLinkSettingsControlPanelEditForm(controlpanel.RegistryEditForm):
    """Settings form for collective.externalizelink
    """
    schema = IExternalizeLinkSettings
    id = "ExternalizeLinkSettingsEditForm"
    label = _(u"Externalize links settings")
    description = _(u"help_externalize_link_settings_editform",
                    default=u"Site configuration for the collective.externalizelink add-on")

    @button.buttonAndHandler(pmf('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.context.REQUEST.RESPONSE.redirect("@@externalizelink-settings")

    @button.buttonAndHandler(pmf('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    def updateWidgets(self):
        super(ExternalizeLinkSettingsControlPanelEditForm, self).updateWidgets()
        self.widgets['links_selection'].rows = 5


class ExternalizeLinkControlPanel(controlpanel.ControlPanelFormWrapper):
    """Externalize link settings control panel
    """
    form = ExternalizeLinkSettingsControlPanelEditForm
    index = ViewPageTemplateFile('controlpanel.pt')

    @property
    @memoize
    def properties_tool(self):
        return getMultiAdapter((self.context, self.request),
                                name=u'plone_tools').properties()

    def check_native_open_popup(self):
        return self.properties_tool.site_properties.external_links_open_new_window=='true'

    def check_native_mark_special_links(self):
        return self.properties_tool.site_properties.mark_special_links=='true'

    def check_themes_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission("Plone Site Setup: Themes", self.context)
