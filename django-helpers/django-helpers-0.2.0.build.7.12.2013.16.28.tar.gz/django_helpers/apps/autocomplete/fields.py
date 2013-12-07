# coding=utf-8
from django import forms
from widgets import AutoCompleteWidget


class AutoCompleteField(forms.Field):
    widget = AutoCompleteWidget

    def __init__(self, lookup, required=True, widget=None, label=None, initial=None,
                 help_text=None, error_messages=None, show_hidden_initial=False,
                 validators=None, localize=False):
        if validators is None:
            validators = []
        if widget is None:
            widget = self.widget(lookup=lookup)
        forms.Field.__init__(self, required, widget, label, initial,
                             help_text, error_messages, show_hidden_initial,
                             validators, localize)
        if isinstance(lookup, type):
            lookup = lookup()
        self.auto_complete = lookup

    def clean(self, value):
        value = forms.Field.clean(self, value)
        auto_complete = self.auto_complete
        try:
            if not value:
                raise
            instance = auto_complete.get_instance(value)
            self.widget.formatted_value = auto_complete.format_value(instance)
            return instance
        except Exception:
            self.widget.formatted_value = ""
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            return None


class SimpleAutoCompleteField(forms.Field):
    widget = AutoCompleteWidget

    def clean(self, value):
        value = forms.Field.clean(self, value)
        self.widget.formatted_value = value
        return value


class ManyToManyAutoCompleteField(forms.Field):
    def __init__(self, lookup, *args, **kwargs):
        forms.Field.__init__(self, *args, **kwargs)
        if isinstance(lookup, type):
            lookup = lookup()
        self.auto_complete = lookup

    def clean(self, value):
        value = forms.Field.clean(self, value)
        try:
            if not value:
                raise
            value = value.split(',')
            auto_complete = self.auto_complete
            instances = auto_complete.get_instances(value)
            self.widget.instances = instances
            return instances
        except Exception:
            self.widget.formatted_value = ""
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            return None