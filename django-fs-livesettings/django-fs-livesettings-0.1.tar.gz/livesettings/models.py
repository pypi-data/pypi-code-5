# coding=utf-8

from django.db import models
from django.db import connection
from django.db.utils import DatabaseError
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from picklefield import fields as picklefield_fields

from livesettings import types as _types
from livesettings import settings as _settings
from livesettings import fields as _fields


class Setting(models.Model):
    TYPE_CHOICES = zip(_types.TYPES, _types.TYPES)

    key = _fields.KeyField(verbose_name=_(u'key'), primary_key=True)
    tpe = models.CharField(verbose_name=_(u'type'), max_length=254, choices=TYPE_CHOICES, blank=True, null=True)
    value = picklefield_fields.PickledObjectField(verbose_name=_(u'value'), editable=True, blank=True, null=True)
    description = models.CharField(verbose_name=_(u'description'), max_length=254, blank=True, null=True)

    class Meta:
        verbose_name = _(u'setting')
        verbose_name_plural = _(u'settings')

    def __unicode__(self):
        return self.key

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Setting, self).save(*args, **kwargs)


def fill_in_settings():
    # whether Setting has been installed or not
    try:
        Setting.objects.exists()
    except DatabaseError:
        connection._rollback()
        return
    try:
        for key, tpe, description in _settings.CONFIG:
            if tpe not in _types.TYPES:
                raise Exception
            if Setting.objects.filter(key=key).update(tpe=tpe, description=description) == 0:
                Setting.objects.create(key=key, tpe=tpe, description=description)
        Setting.objects.exclude(key__in=[conf[0] for conf in _settings.CONFIG]).delete()
    except:
        raise ImproperlyConfigured(u'LiveSettings is improperly configured.')


fill_in_settings()
