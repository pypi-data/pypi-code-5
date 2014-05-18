
from django.contrib import admin
from cloudengine.core.models import CloudAPI
from cloudengine.auth.models import Token


class CloudAPIAdmin(admin.ModelAdmin):
    list_display = ('date', 'count', 'app')
    #list_filter = ('caller__user__username',)

admin.site.register(CloudAPI, CloudAPIAdmin)
admin.site.register(Token)