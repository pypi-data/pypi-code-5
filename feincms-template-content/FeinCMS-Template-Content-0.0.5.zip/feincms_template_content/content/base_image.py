from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible

from feincms_template_content.models import TemplateContent


@python_2_unicode_compatible
class BaseImageContent(TemplateContent):
    class Meta(object):
        abstract = True
        verbose_name = _('image')
        verbose_name_plural = _('images')

    template_choices = (
        ('content/image/block.html', 'Block'),
        ('content/image/float_left.html', 'Float left'),
        ('content/image/float_right.html', 'Float right'),
    )

    def get_file(self):
        return self.image

    def __str__(self):
        return u"%s" % self.get_file()
