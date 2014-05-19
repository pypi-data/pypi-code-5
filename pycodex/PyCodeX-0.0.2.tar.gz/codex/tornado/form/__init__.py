from wtforms import *

class FormDataMultiDict(object):

    def __init__(self, multidict):
        self._wrapped = multidict

    def __iter__(self):
        return iter(self._wrapped)

    def __len__(self):
        return len(self._wrapped)

    def __contains__(self, name):
        return (name in self._wrapped)

    def __getitem__(self, name):
        return self._wrapped[name]

    def __getattr__(self, name):
        return self.__getitem__(name)

    def getlist(self, name):
        if name not in self._wrapped:
            return []
        if isinstance(self._wrapped[name], list):
            return self._wrapped[name]
        return [self._wrapped[name]]

class RequestForm(Form):
    def __init__(self, controller, formdata=None, obj=None, prefix='', **kwargs):
        self._delimiter_start = '<p>'
        self._delimiter_end = '</p>'
        self.controller = controller
        super().__init__(FormDataMultiDict(formdata), obj, prefix, **kwargs)

    def set_error_delimiter(self, start, end):
        self._delimiter_start = start
        self._delimiter_end = end

    def validation_errors(self):
        errors = []
        for field_id in self.errors.keys():
            field = self._fields[field_id]
            for e in self.errors[field_id]:
                errors.append(e.replace('{{field_label}}', field.label.text))
        return self._delimiter_start + (self._delimiter_end + self._delimiter_start).join(errors) + self._delimiter_end