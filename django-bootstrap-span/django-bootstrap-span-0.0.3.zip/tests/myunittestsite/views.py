"""
myunittestsite.views  django-bootstrap-span/tests/myunittestsite/views.py.
(C) Copyright 2014 Stuart McMillan, Useful Automation
"""

from bootstrap.views import FormView
from bootstrap_span.form_span import view_form_with_bootstrap_span,\
    FormSpanMixin
from myunittestsite.forms import form_class_creator
from django.core.urlresolvers import reverse_lazy

@view_form_with_bootstrap_span() #pylint: disable=no-init,too-few-public-methods
class DecoratedViewClass(FormView):
    "Decorated form class for form span testing"
    template_name = 'myunittestsite/form_template.html'
    form_class = form_class_creator()
    success_url = reverse_lazy('home')

    def get_success_url(self):
        '''Where to go on success'''
        return DecoratedViewClass.get_success_url

    def get_context_data(self, *args, **kwargs):
        "Build context for call - side effect perform image construction"
        context = super(DecoratedViewClass, self).get_context_data(*args, **kwargs)
        context['max_spans_comma_chars_per_span_string'] = ''
        context['do_span_filter'] = False
        return context

class MixinViewClass(FormSpanMixin,FormView):#pylint: disable=no-init,too-many-public-methods
    "Decorated form class for form span testing"
    template_name = 'myunittestsite/form_template.html'
    form_class = form_class_creator()
    success_url = reverse_lazy('home')

    def get_success_url(self):
        '''Where to go on success'''
        return MixinViewClass.get_success_url

    def get_context_data(self, *args, **kwargs):
        "Build context for call - side effect perform image construction"
        context = super(MixinViewClass, self).get_context_data(*args, **kwargs)
        context['max_spans_comma_chars_per_span_string'] = ''
        context['do_span_filter'] = False
        return context
