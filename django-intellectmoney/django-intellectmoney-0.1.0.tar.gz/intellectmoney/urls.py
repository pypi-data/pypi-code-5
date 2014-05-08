# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^result/$',  views.receive_result, name='intellectmoney-result'),
    url(r'^success/$',  views.success, name='intellectmoney-success'),
    url(r'^fail/$',  views.fail, name='intellectmoney-fail'),

)
