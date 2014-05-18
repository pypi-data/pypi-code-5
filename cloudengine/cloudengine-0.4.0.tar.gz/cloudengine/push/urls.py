from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from cloudengine.push.views import AppPushView
from cloudengine.decorators import admin_view

# todo: rest api -- allow traversing api through urls??

urlpatterns = patterns('',
                       # Examples:
                       #url(r'^$', FileList.as_view(), name="files-app-home"),
                       # todo: the regex decides the allowed filenames.
                       # standardize filenames
                       # todo: add testcases for all possible filenames
                       url(r'^$', admin_view(AppPushView.as_view()), 
                           name="cloudengine-app-push"),
                      )

urlpatterns = format_suffix_patterns(urlpatterns)
