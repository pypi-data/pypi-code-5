"""
myunittestsite.models  django-bootstrap-span/tests/myunittestsite/models.py.
(C) Copyright 2014 Stuart McMillan, Useful Automation
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

def model_class_creator(model_field_type=models.CharField,max_length=60):
    "Create a type changing db model"
    class TestModel(models.Model):
        """
        TestUserModel class.
        """
        data_field = model_field_type(_("Data field"),
                                max_length=max_length,
                                null=False,
                                blank=False,
                                default=_("Data field default"),
                                help_text=_("The data field."),
                                unique=True)

    return TestModel

