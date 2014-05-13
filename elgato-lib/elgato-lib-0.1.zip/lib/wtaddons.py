__author__ = 'dsedad'

from wtforms import TextField as TextField


class DisabledTextField(TextField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('disabled', True)
        return super(DisabledTextField, self).__call__(*args, **kwargs)

  # def __call__(self, *args, **kwargs):
  #   kwargs.setdefault('disabled', True)
  #   return super(DisabledTextField, self).__call__(*args, **kwargs)
