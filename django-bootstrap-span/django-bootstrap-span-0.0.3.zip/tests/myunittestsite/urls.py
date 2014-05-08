"""
myunittestsite.urls  django-bootstrap-span/tests/urls.py.
(C) Copyright 2014 Stuart McMillan, Useful Automation
"""
#pylint: disable=no-value-for-parameter
from django.conf.urls import patterns, include, url

from myunittestsite import views

urlpatterns = patterns( '',

    url(r'^home/$', views.DecoratedViewClass.as_view(), name='home'),
    url(r'^mixin/$', views.MixinViewClass.as_view(), name='mixin'),
    url(r'^tinymce/', include('tinymce.urls')),
)
