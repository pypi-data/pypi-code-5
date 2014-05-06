from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from feincms.admin.item_editor import FeinCMSInline

from feincms.module.medialibrary.fields import MediaFileForeignKey

from .base_image import BaseImageContent


class MedialibraryImageContent(BaseImageContent):
    class Meta(object):
        abstract = True
        verbose_name = _('image')
        verbose_name_plural = _('images')

    class feincms_item_editor_inline(FeinCMSInline):
        raw_id_fields = ('image',)

    image = MediaFileForeignKey(
        'medialibrary.MediaFile',
        verbose_name=_('image'),
        related_name='+',
    )

    def clean(self, *args, **kwargs):
        if self.image.type != 'image':
            raise ValidationError('Chosen media file is not an image')

        return super(MedialibraryImageContent, self).clean(*args, **kwargs)

    def get_file(self):
        return self.image.file
