from django.conf.urls import patterns, url
from isegory import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'isegory.views',
    url(r'^$',
        'index',
        name='index'),

    url(r'^poderes/(?P<slug>[\w-]+)/*$',
        views.PowerDetail.as_view(),
        name='power_detail'),

    url(r'^poderes/$',
        views.PowerList.as_view(),
        name='power_list'),

    url(r'^personas/',
        views.PersonList.as_view(),
        name='person_list'),

    url(r'^organos/',
        views.OrganList.as_view(),
        name='organ_list'),

    url(r'^informacion/',
        views.InformationList.as_view(),
        name='information_list'),

    url(r'^conjuntos-de-datos/(?P<slug>[\w-]+)/*$',
        views.DataDetail.as_view(),
        name='data_detail'),

    url(r'^conjuntos-de-datos/',
        views.DataList.as_view(),
        name='data_list'),

    url(r'^docs/$',
        'docs',
        name='docs'),
)
