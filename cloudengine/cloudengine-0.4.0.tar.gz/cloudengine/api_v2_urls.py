from django.conf.urls import patterns, url, include
from cloudengine.core.api import AppView, AppListView, APICallView

urlpatterns = patterns('',

                       url(r'^classes/', include('cloudengine.classes.api_v2_urls')),
                       url(r'^files/', include('cloudengine.files.api_v2_urls')),
                       url(r'^push/', include('cloudengine.push.api_v2_urls')),
                       url(r'^apps/(?P<name>[a-zA-Z0-9]+)/$',
                           AppView.as_view()),
                       url(r'^apps/$', AppListView.as_view()),
                       url(r'^users/', include('cloudengine.users.api_v2_urls')),
                       url(r'^apicalls/$', APICallView.as_view())
                       )
