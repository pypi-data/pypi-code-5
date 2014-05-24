from django.conf.urls import patterns, include, url
from bambu_api import autodiscover, site

autodiscover()
urlpatterns = patterns('',
	url(r'^', include(site.urls))
)