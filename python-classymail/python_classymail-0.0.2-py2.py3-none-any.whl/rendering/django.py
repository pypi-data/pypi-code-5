from __future__ import absolute_import

from django.template.loader import render_to_string
from classymail.rendering import BaseRenderer

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class DjangoRenderer(BaseRenderer):
    def render(self, template, context=None):
        return render_to_string(template, context)