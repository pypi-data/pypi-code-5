# coding=utf-8

from livesettings import models as _models


class LiveSettings(object):
    def __getattr__(self, name):
        try:
            setting = _models.Setting.objects.get(key=name)
            return setting.value
        except _models.Setting.DoesNotExist:
            raise AttributeError('\'{0}\' object has no attribute \'{1}\''.format(type(self).__name__, name))


livesettings = LiveSettings()
