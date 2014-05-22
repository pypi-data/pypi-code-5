from django.conf.urls import url, patterns
from avclub.apps.feeds.views import RSSView


urlpatterns = patterns("",
    url(r"^rss", RSSView.as_view())  # noqa
)
