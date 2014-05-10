from django.db import models

class Edito(models.Model):
    TEXT_THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
    )
    title = models.CharField(max_length=100)
    link = models.URLField()
    image = models.FileField(upload_to="editos")
    text_content = models.CharField(max_length=400)
    display_from = models.DateField()
    display_until = models.DateField()
    active = models.BooleanField(default=True)
    text_theme = models.CharField(max_length=10, choices=TEXT_THEME_CHOICES,
            default='light', help_text="light if the image is dark, dark if the image is light")

    def __unicode__(self):
        return self.title
