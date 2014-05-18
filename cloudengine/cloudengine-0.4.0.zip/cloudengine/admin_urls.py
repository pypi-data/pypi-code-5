from django.conf.urls import patterns, url, include
from cloudengine.decorators import admin_view
from cloudengine.core.views import (CreateAppView, 
                AdminHomeView, AppSettingsView,
                AppsBrowser)

urlpatterns = patterns('',

                        url(r'^$', admin_view (AdminHomeView.as_view()), 
                            name="cloudengine-admin-home"),
                        
                        url(r'^create_app/$', CreateAppView.as_view()),
                       
                       url(r'^classes/', 
                            include('cloudengine.classes.urls')),
                       
                       url(r'^files/', 
                            include('cloudengine.files.urls')),
                       
                       url(r'^push/$', 
                            include('cloudengine.push.urls')),
                       
                       url(r'^users/$', 
                            include('cloudengine.users.urls')),
                       
                       url(r'^apps/$', admin_view(AppsBrowser.as_view()), 
                            name="cloudengine-apps-browser"),
                       
                        url(r'^apps/(?P<app_name>[a-zA-Z0-9]+)/$', 
                                    admin_view(AppSettingsView.as_view()), name='cloudengine-app-settings'),
    
                     
                       )
