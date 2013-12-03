"""
sentry.models.groupbookmark
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.conf import settings
from django.db import models

from sentry.db.models import Model, BaseManager, sane_repr


class GroupBookmark(Model):
    """
    Identifies a bookmark relationship between a user and an
    aggregated event (Group).
    """
    project = models.ForeignKey('sentry.Project', related_name="bookmark_set")
    group = models.ForeignKey('sentry.Group', related_name="bookmark_set")
    # namespace related_name on User since we don't own the model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sentry_bookmark_set")

    objects = BaseManager()

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_groupbookmark'
        # composite index includes project for efficient queries
        unique_together = (('project', 'user', 'group'),)

    __repr__ = sane_repr('project_id', 'group_id', 'user_id')
