from django.conf.urls import patterns, url
from cloudengine.classes.views import AppDataView
from cloudengine.decorators import admin_view



urlpatterns = patterns('',

                       url(r'^$', 
                            admin_view(AppDataView.as_view()), name="cloudengine-app-data"),
                     
                       )
