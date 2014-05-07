#encoding=utf-8

from django.contrib import admin
from molp.models import Parameter


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description', 'version', 'channel', 'effect_time')
    list_filter = ('app', 'channel', 'version')

    search_fields = ('name', 'value', 'description')


admin.site.register(Parameter, ParameterAdmin)
