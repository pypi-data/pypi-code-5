from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .base_image import BaseImageContent


class ImageContent(BaseImageContent):
    class Meta(object):
        abstract = True
        verbose_name = _('image')
        verbose_name_plural = _('images')

    image = models.ImageField(upload_to='feincms')
