# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from . import get_register_model, get_register_form_fields


class RegisterForm(forms.ModelForm):
    """
    RegisterForm is intended to be a highly customizable ModelForm and
    the user can change the model associated to the form and form fields
    """

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Submit')))
        super(RegisterForm, self).__init__(*args, **kwargs)

    class Meta:
        model = get_register_model()
        fields = get_register_form_fields()
