"""
Form span utility.
(C) Copyright 2014 Stuart McMillan, Useful Automation
"""
import re
import six

from django.core import validators

DEFAULT_CHARS_PER_SPAN = 5
DEFAULT_MAX_SPAN = 12

class FormSpanMixin(object):
    """Bootstrap form utility which adds file class spanN (indicating field length)"""
    LENGTH_RE = re.compile(r'\b(?:maxlength|cols)\s*=\s*"(\d+)"',re.IGNORECASE|re.MULTILINE)

    def __init__(self,max_span=None,chars_per_span=None,*args,**kwargs):
        super(FormSpanMixin,self).__init__(*args,**kwargs)
        if max_span == None:
            self.max_span=DEFAULT_MAX_SPAN
        else:
            self.max_span = max_span
        if chars_per_span == None:
            self.chars_per_span = DEFAULT_CHARS_PER_SPAN
        else:
            self.chars_per_span = chars_per_span

    def get_form(self,*args,**kwargs):
        '''
        get form method overrides inherited method - and adjust forms (for mixin)
        '''
        the_form = super(FormSpanMixin,self).get_form(*args,**kwargs)
        self.alter_form_fields_class_span(the_form)
        return the_form

    def alter_form_fields_class_span(self,target_form_instance):
        """Customise each field in target_form_instance with correct span"""
        #print target_form_instance.fields
        for field_name,field_instance in six.iteritems(target_form_instance.fields):
            # Try to find attribute of maximum length
            max_length = self.check_field_max_length_attributes(field_instance)
            # Try to find validator of maximum length
            if max_length == 0:
                max_length = self.check_field_max_length_validators(field_instance)
                # Examine HTML attributes for length fields
            if max_length == 0:
                s = str(target_form_instance[field_name])
                max_length = self.check_field_generated_html(s)
            # Apply the span
            if  max_length is not None and max_length > 0 :
                span_width = max(1,min(self.max_span,int(int(max_length+(self.chars_per_span-1))/
                                                         self.chars_per_span)))
                new_span_class = "span%s"%span_width
                new_class_list = ''
                if 'class' in target_form_instance.fields[field_name].widget.attrs:
                    new_class_list = (
                        target_form_instance.fields[field_name].widget.attrs['class']+" " )
                # Apply class to the widget
                target_form_instance.fields[field_name].widget.attrs['class'] =(
                    new_class_list+new_span_class )
                #print field_instance
    @staticmethod
    def check_field_max_length_attributes( field):
        """Some fields have max_length as n attribute - check for that"""
        max_length = getattr(field,'max_length',0)
        if max_length:
            return max_length
        return 0
    @staticmethod
    def check_field_generated_html(generated_html):
        """Look inside HTML for fields for 'maxlength' or 'cols' values"""
        match = FormSpanMixin.LENGTH_RE.search(generated_html)
        if match:
            return int(match.group(1))
    @staticmethod
    def check_field_max_length_validators(field):
        """Check for a validator which know the string max length"""
        if getattr(field,'validators',None) == None:
            return 0
        max_length_validators = [ v for v in field.validators
                                 if isinstance(v,validators.MaxLengthValidator) ]
        max_length_values = [ v.limit_value for v in max_length_validators ]
        #print max_length_values
        if not max_length_validators:
            return 0
        return max(max_length_values)

def view_form_with_bootstrap_span(max_span=None,chars_per_span=None):
    """Decorator for applying bootstrap span class to a View containing forms"""
    formSpanner = FormSpanMixin(max_span=max_span,chars_per_span=chars_per_span)

    def decorator(target_class):
        """This is the class decorator function for applying the span class to the form
        via the View's get_form function."""
        old_get_form = getattr(target_class,'get_form')
        def get_form(self,form_class):
            """Returns the form to use in this view"""
            form = old_get_form(self,form_class)
            formSpanner.alter_form_fields_class_span(target_form_instance=form)
            return form
        setattr(target_class,'get_form',get_form)
        return target_class
    return decorator
