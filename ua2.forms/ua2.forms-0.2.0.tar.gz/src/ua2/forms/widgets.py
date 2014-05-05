from django.forms import Select

class SelectCallback(Select):
    def __init__(self, attrs=None):
        super(Select, self).__init__(attrs)
        self.choices_callback = None

    def render(self, name, value, attrs=None):
        self.choices = list(self.choices_callback())
        return super(SelectCallback, self).render(name, value, attrs)
