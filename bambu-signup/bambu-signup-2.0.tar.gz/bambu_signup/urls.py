from django.conf.urls import patterns, url
from bambu_signup.views import *
from bambu_signup.views import ajax
from django.conf import settings

if 'bambu_bootstrap' in settings.INSTALLED_APPS:
    from bambu_bootstrap.decorators import body_classes
else:
    def body_classes(view, *classes):
        return view

urlpatterns = patterns('',
    url(r'^signup/$', body_classes(register, 'signup'), name = 'signup'),
    url(r'^signup/complete/$',
        body_classes(register_complete, 'signup', 'signup-complete'), name = 'signup_complete'
    ),
    url(r'^login/$', login, name = 'login'),
    url(r'^logout/$', logout, name = 'logout'),
    url(r'^verify/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        body_classes(verify_email, 'signup-verify'), name = 'verify_email'
    ),
    url(r'^reset/$', body_classes(reset_password, 'signup-reset'), name = 'forgot_password'),
    url(r'^reset/(?P<guid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$',
        body_classes(reset_password, 'signup-reset', 'signup-reset-result'), name = 'reset_password'
    ),
    url(r'^ajax/username-exists\.js$', ajax.username_exists, name = 'username_exists_ajax'),
    url(r'^ajax/email-exists\.js$', ajax.email_exists, name = 'email_exists_ajax')
)