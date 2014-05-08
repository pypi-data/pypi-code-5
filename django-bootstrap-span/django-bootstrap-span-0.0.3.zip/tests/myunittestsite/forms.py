"""
myunittestsite.models  django-bootstrap-span/tests/myunittestsite/forms.py.
(C) Copyright 2014 Stuart McMillan, Useful Automation
"""
from django import forms as fforms
from django.db import models as dbmodels
from myunittestsite.models import model_class_creator

def form_class_creator(max_length=254,
                             field_type=fforms.EmailField,
                             model_field_type=dbmodels.CharField):
    "create a class with specific max length attributes and field type"

    class CreateForm(fforms.ModelForm):# pylint: disable=too-few-public-methods,no-init

        "Create for for test model/data field"
        data_field = field_type(max_length=max_length)
        #label=_("Email address")
        #min_length=min_length

        class Meta:# pylint: disable=no-init,too-few-public-methods,old-style-class,missing-docstring
            model = model_class_creator(model_field_type=model_field_type)
            fields = ['data_field',
                      #'first_name','last_name'
            ]

    class CreateFormPassThrough(fforms.ModelForm):# pylint: disable=too-few-public-methods,no-init

        "Create form delegates to test model"

        class Meta:# pylint: disable=no-init,too-few-public-methods,old-style-class,missing-docstring
            model = model_class_creator(model_field_type=model_field_type,
                                        max_length=max_length)
            fields = ['data_field',
                      #'first_name','last_name'
            ]


    if model_field_type==dbmodels.CharField:
        return CreateForm
    return CreateFormPassThrough
