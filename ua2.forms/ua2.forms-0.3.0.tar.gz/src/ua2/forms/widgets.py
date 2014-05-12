from django.forms import Select, DateInput


class SelectCallback(Select):
    def __init__(self, attrs=None):
        super(Select, self).__init__(attrs)
        self.choices_callback = None

    def render(self, name, value, attrs=None):
        self.choices = list(self.choices_callback())
        return super(SelectCallback, self).render(name, value, attrs)


class DatePickerWidget(DateInput):
    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(DatePickerWidget, self).build_attrs(extra_attrs, **kwargs)
        attrs['class'] = attrs.get('class', '') + ' date-picker'
        attrs['data-date-autoclose'] = 'true'
        attrs['data-date-format'] = self.format.replace('y', 'yy')\
            .replace('Y', 'yyyy')\
            .replace('M', 'mm')\
            .replace('D', 'dd')\
            .replace('%', '')
        return attrs
