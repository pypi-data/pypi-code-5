# coding=utf-8

import re

from django.db.models.fields import CharField
from django.core.validators import RegexValidator


key_re = re.compile(r'^[a-zA-Z0-9_]+$')
validate_key = RegexValidator(key_re, u'Enter a valid key.', 'invalid')


class KeyField(CharField):
    default_validators = [validate_key]

    def __init__(self, *args, **kwargs):
        assert kwargs.get('primary_key', False) is True, '%ss must have primary_key=True.' % self.__class__.__name__
        kwargs['max_length'] = kwargs.get('max_length', 254)
        CharField.__init__(self, *args, **kwargs)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        cls_name = '{0}.{1}'.format(self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return cls_name, args, kwargs
