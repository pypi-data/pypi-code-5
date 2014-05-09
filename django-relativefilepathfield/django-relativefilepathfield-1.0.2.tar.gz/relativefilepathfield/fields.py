from __future__ import absolute_import
import os
from django.db.models.fields import FilePathField
from relativefilepathfield import forms

class AbsPath(object):

    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))

        return lambda: os.path.join(self.field.path, instance.__dict__[self.field.name])

class RelativeFilePathField(FilePathField):
    
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.RelativeFilePathField,
        }
        defaults.update(kwargs)
        return super(RelativeFilePathField, self).formfield(**defaults)
    
    def contribute_to_class(self, cls, name):
        super(RelativeFilePathField, self).contribute_to_class(cls, name)
        setattr(cls, 'get_%s_abspath' % self.name, AbsPath(self))

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^relativefilepathfield\.fields\.RelativeFilePathField"])
except ImportError: pass