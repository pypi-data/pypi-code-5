from __future__ import absolute_import
import os
from django.forms.fields import FilePathField

class RelativeFilePathField(FilePathField):
    def __init__(self, path, *args, **kwargs):
        super(RelativeFilePathField, self).__init__(path, *args, **kwargs)
        choices = []
        for choice in self.choices:
            choices.append((os.path.relpath(choice[0], path), choice[1]))
        self.choices = choices