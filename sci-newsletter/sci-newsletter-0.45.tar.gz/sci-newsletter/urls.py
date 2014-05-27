from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^job/(\d+)/?', 'newsletter.views.job', name='job'),
	url(r'^jobs/?', 'newsletter.views.job_list', name='job_list'),
	url(r'^feed/?', 'newsletter.views.feed', name='feed'),
	url(r'^newjob/?', 'newsletter.views.new_job', name='new_job'),
	url(r'^archive/?', 'newsletter.views.archive', name='archive'),
	url(r'^preview/(\d+)/?', 'newsletter.views.job_preview', name='preview'),
	url(r'^preview_last/?', 'newsletter.views.job_preview_last', name='preview_last'),
	url(r'^ajax_recievers/?', 'newsletter.views.get_recievers', name='ajax_recievers'),
)