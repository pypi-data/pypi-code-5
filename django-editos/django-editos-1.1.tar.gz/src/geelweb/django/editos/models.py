from django.db import models
from geelweb.django.editos import settings

class Edito(models.Model):
    title = models.CharField(max_length=100,
            help_text=settings.EDITOS_HELP_TEXTS.get('title'))
    link = models.URLField(help_text=settings.EDITOS_HELP_TEXTS.get('link'))
    button_label = models.CharField(max_length=20, default="Go !",
            blank=True, help_text=settings.EDITOS_HELP_TEXTS.get('button_label'))
    image = models.FileField(upload_to="editos",
            help_text=settings.EDITOS_HELP_TEXTS.get('image'))
    text_content = models.CharField(max_length=400,
            help_text=settings.EDITOS_HELP_TEXTS.get('text_content'))
    display_from = models.DateField(help_text=settings.EDITOS_HELP_TEXTS.get('display_from'))
    display_until = models.DateField(help_text=settings.EDITOS_HELP_TEXTS.get('display_until'))
    active = models.BooleanField(default=True, help_text=settings.EDITOS_HELP_TEXTS.get('active'))
    text_theme = models.CharField(max_length=10, choices=settings.EDITOS_THEMES,
            default=settings.EDITOS_DEFAULT_THEME,
            help_text=settings.EDITOS_HELP_TEXTS.get('text_theme'))

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title
