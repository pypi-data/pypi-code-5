from django.conf.urls import patterns, url
from cloudengine.files.views import (AppFilesView,
                        download_file)
from cloudengine.decorators import admin_view

# todo: rest api -- allow traversing api through urls??

urlpatterns = patterns('',
                       # Examples:
                       #url(r'^$', FileList.as_view(), name="files-app-home"),
                       # todo: the regex decides the allowed filenames.
                       # standardize filenames
                       # todo: add testcases for all possible filenames
                       url(r'^$', admin_view(AppFilesView.as_view()),
                          name="cloudengine-app-files"),
                       url(r'^upload/$', admin_view(AppFilesView.as_view()),
                           name="cloudengine-app-files-upload"),
                       url(r'^download/(?P<appname>[a-zA-Z0-9]+)/(?P<filename>.+)/$', 
                           admin_view(download_file),
                           name="cloudengine-download-file"),
                       )

