"""
Add a many-to-many relationship field to relate this page to other pages.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from feincms import extensions, settings


class Extension(extensions.Extension):
    def handle_model(self):
        self.model.add_to_class('related_pages', models.ManyToManyField(
            settings.FEINCMS_DEFAULT_PAGE_MODEL,
            blank=True,
            null=True,
            related_name='%(app_label)s_%(class)s_related',
            help_text=_(
                'Select pages that should be listed as related content.')))

    def handle_modeladmin(self, modeladmin):
        modeladmin.filter_horizontal = list(
            getattr(modeladmin, 'filter_horizontal', ()))
        modeladmin.filter_horizontal.append('related_pages')

        modeladmin.add_extension_options(_('Related pages'), {
            'fields': ('related_pages',),
            'classes': ('collapse',),
        })
