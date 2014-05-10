# coding=utf-8

from django.contrib import admin

from livesettings import models as _models
from livesettings import forms as _forms


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'tpe', 'value', 'description')
    fields = ('key', 'tpe', 'value', 'description')
    readonly_fields = ('key', 'tpe', 'description')
    actions = None
    form = _forms.SettingAdminForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(_models.Setting, SettingAdmin)
