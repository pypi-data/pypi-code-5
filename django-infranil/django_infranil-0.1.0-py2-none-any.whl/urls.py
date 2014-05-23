from django.conf.urls import patterns
from .views import InfranilView


urlpatterns = patterns(
    '',
    (r'^(?P<path>.*)$', InfranilView.as_view()),
)
