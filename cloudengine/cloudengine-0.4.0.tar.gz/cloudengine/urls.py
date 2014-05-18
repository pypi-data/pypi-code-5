from django.conf.urls import patterns, include, url
from cloudengine.core.views import AccountKeysView
from django.views.generic import TemplateView
from cloudengine.decorators import admin_view
from cloudengine.core.views import AppsBrowser

urlpatterns = patterns(
    '',
    # Examples:
    
    url(r'^$', TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'^admin/', include('cloudengine.admin_urls')),
    url(r'^api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),
    url(r'^socket.io/', 'cloudengine.push.views.socketio_view'),
    url(r'^api/v2/', include('cloudengine.api_v2_urls')),
    url(r'^keys/$',
        AccountKeysView.as_view(), name='myaccount-keys'),
    url(r'^accounts/', include(
        'registration.backends.simple.urls')),

)
