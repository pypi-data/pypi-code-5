# coding=utf-8

from django.conf import settings


CONFIG = getattr(settings, 'LIVESETTINGS_CONFIG', {})
