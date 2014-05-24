from django.conf.urls import url, patterns
from bambu_xmlrpc import autodiscover

autodiscover()
urlpatterns = patterns('bambu_xmlrpc.views',
    url(r'^$', 'dispatch', name = 'xmlrpc_server')
)