'''
test_single_field  django-bootstrap-span/tests/test_single_field.py.
(C) Copyright 2014 Stuart McMillan, Useful Automation
'''

import os
import sys
import codecs

sys.path.append(os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = "myunittestsite.settings"

import unittest
from myunittestsite.forms import form_class_creator

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django import forms as fforms
from django.db import models

from django.test.utils import setup_test_environment
from django.test.client import Client

class TestSingleField(unittest.TestCase):# pylint: disable=too-many-public-methods,no-init
    "Simple test framework"

    def setUp(self):
        setup_test_environment()
        self.client = Client()
        self.max_spans = 12
        self.chars_per_span = 5
        self.field_type = fforms.EmailField
        self.model_field_type = models.CharField
        self.form = form_class_creator()
        self.use_max_span = True
        self.use_chars_per_span = True

    def tearDown(self):
        pass

    def span_width(self,field_char_width):
        '''
        calculate expected span width for a given field character width situation
        :param field_char_width:
        '''
        span_count = int((field_char_width+(self.chars_per_span-1))/self.chars_per_span)
        span_count = min(span_count,self.max_spans)
        return "span"+str(span_count)

    def testOneField(self,width_value=254,span_width_count=1,do_span_filter=True):
        '''
        simple field test  - form with one field - check it has a spanN class -
        exactly one (or span_width_count)
        '''
        template_dict =  {
                  'do_span_filter' : do_span_filter,
                  'form': self.form,
                  "max_spans":self.max_spans,
                  "chars_per_span":self.chars_per_span,
                  "max_spans_comma_chars_per_span_string": "%s,%s"%(
                        self.max_spans if self.use_max_span else "",
                        self.chars_per_span if self.use_chars_per_span else "")
                }

        rendered = render_to_string('myunittestsite/form_template.html',
                template_dict
        )
        self._check_n_span_in_container(width_value,rendered,
                                         span_width_count=span_width_count)

    def _check_n_span_in_container(self,width_value,container,span_width_count=1):
        '''
        check span class was applied N count times
        :param width_value:
        :param container:
        :param span_width_count:
        '''
        span_widths = self.span_width(width_value)
        self.assertIn(member=span_widths,
                      container=container
                      )
        self.assertEqual(container.count(span_widths),
                         span_width_count,
                         "unexpected class span counts")

    def testDoubleFormCall(self):
        '''
        double usage of form in template
        '''
        self.testOneField()
        self.testOneField(span_width_count=1)

    def testCustomFieldWidths(self,char_width_steps=1):
        '''
        custom field widths test
        '''
        for field_width in range(1,(self.max_spans+1)*(self.chars_per_span),char_width_steps):
            self.form = form_class_creator(max_length=field_width,
                                           field_type=self.field_type,
                                           model_field_type=self.model_field_type)
            self.testOneField(width_value=field_width)

    def testCustomMaxSpansFieldWidths(self):
        "Customer max_spans tests"
        self.max_spans = 11
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.max_spans = 9
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.max_spans = 6
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.max_spans = 3
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.max_spans = 1
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)

    def testCustomCharsPerSpanFieldWidths(self):
        "Custom chars_per_span tests"
        self.chars_per_span = 10
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.chars_per_span = 9
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.chars_per_span = 6
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.chars_per_span = 3
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)
        self.chars_per_span = 1
        self.testCustomFieldWidths(char_width_steps=self.chars_per_span)

    ALL_FIELD_TYPES =  [ fforms.CharField,
#                         fforms.CheckboxInput,
#                         fforms.CheckboxSelectMultiple,
#                         fforms.TimeField,
#                         fforms.DateField,
#                         fforms.Textarea,
#                         fforms.TextInput,
                         fforms.FileField,
                         lambda **kwarg : fforms.RegexField(regex=r"\w*",**kwarg), # needs regex pylint: disable=star-args
                         fforms.URLField,
                         fforms.EmailField,
    ]

    def testAllFormFieldTypes(self):
        "Try all the field types"
        for field_type in TestSingleField.ALL_FIELD_TYPES:
            self.field_type=field_type
            self.testCustomFieldWidths(char_width_steps=self.chars_per_span)

    ALL_MODEL_FIELD_TYPES = [
    ]

    def testAllModelFieldTypes(self):
        "Try all the field types"
        from tinymce import models as tinymce_models
        TestSingleField.ALL_MODEL_FIELD_TYPES.append(tinymce_models.HTMLField)
        for model_field_type in TestSingleField.ALL_MODEL_FIELD_TYPES:
            self.model_field_type=model_field_type
            self.testCustomFieldWidths(char_width_steps=59)

    def testWithParameterCombinationDefaults(self):
        '''
        default parameter usage of form in template
        '''
        # max span and chars per span - defaulted
        self.use_max_span = False
        self.use_chars_per_span = False
        self.testOneField()
        # max span - defaulted
        self.use_max_span = True
        self.use_chars_per_span = False
        self.testOneField()
        # chars per span - defaulted
        self.use_max_span = False
        self.use_chars_per_span = True
        self.testOneField()

    def testWithDecoratedFormView(self):
        '''
        default parameter usage of form in view class template
        '''
        # pylint: disable=maybe-no-member
        # find the view
        self.max_spans = 12
        self.chars_per_span = 5

        request_url = reverse('home')
        response = self.client.get(request_url)

        self.assertIn("span",
            codecs.decode(response.content,"utf8")+':'+
            str(response.status_code)+':'+
            str(request_url))

        self._check_n_span_in_container(width_value=254,
            container=codecs.decode(response.content,"utf8"),
            span_width_count=1)

    def testLevelsOfFieldWidthDiscovery(self):
        '''
        default parameter usage of form in template
        '''
        # pylint: disable=maybe-no-member
        def empty_widget_attr():
            '''
            Set the widget attr to be empty
            '''
            self.form.fields['data_field'].widget.attrs['class']=''
            return None

        discovery_adjustments=(
            lambda : setattr(self.form.fields['data_field'],'max_length',None),

            lambda : ( setattr(self.form.fields['data_field'],'max_length',None),
                       setattr(self.form.fields['data_field'],'validators',[]) ),

            lambda : ( setattr(self.form.fields['data_field'],'max_length',None),
                       setattr(self.form.fields['data_field'],'validators',None) ),

            lambda : ( setattr(self.form.fields['data_field'],'validators',[]) ),

            empty_widget_attr

        )
        # Test each adjusted scenario
        for discovery_adjustment in discovery_adjustments:
            self.setUp()
            self.form = self.form()
            discovery_adjustment()
            self.testOneField()

    def testWithMixinFormView(self):
        '''
        default parameter usage of form in view class template
        '''
        # pylint: disable=maybe-no-member
        # find the view
        self.max_spans = 12
        self.chars_per_span = 5

        request_url = reverse('mixin')
        response = self.client.get(request_url)

        self.assertIn("span",
            codecs.decode(response.content,"utf8")+':'+
            str(response.status_code)+':'+
            str(request_url))

        self._check_n_span_in_container(width_value=254,
            container=codecs.decode(response.content,"utf8"),
            span_width_count=1)
