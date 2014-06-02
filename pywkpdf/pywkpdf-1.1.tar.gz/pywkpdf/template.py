# encoding=utf-8
import logging
from os import path
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from . import html_to_pdf, html_to_pdf_file


log = logging.getLogger('pywkpdf')


def render_to_pdf(template_name, dictionary=None,
                  context_instance=None, convert_args=None):
    convert_args = convert_args or {}
    html = _render_template(template_name, dictionary, context_instance)
    return html_to_pdf(html, **convert_args)


def render_to_file(template_name, file_name, dictionary=None,
                   context_instance=None, convert_args=None):
    convert_args = convert_args or {}
    html = _render_template(template_name, dictionary, context_instance)
    return html_to_pdf_file(html, file_name, **convert_args)


def render_to_response(request, template_name, dictionary=None,
                       file_name=None, convert_args=None):
    pdf_file = render_to_pdf(
        template_name, dictionary, RequestContext(request), convert_args)
    pdf_size = path.getsize(pdf_file.name)

    log.debug('generated a PDF file, location: %s, size: %s',
              pdf_file.name, pdf_size)

    response = HttpResponse(
        FileWrapper(pdf_file), content_type='application/pdf')
    if file_name:
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
            file_name)
    else:
        response['Content-Disposition'] = 'attachment'
    response['Content-Length'] = pdf_size
    pdf_file.seek(0)

    return response


def _render_template(template_name, dictionary, context_instance):
    new_dictionary = {
        'STATIC_URL': settings.STATIC_ROOT,
        'PROJECT_PATH': settings.PROJECT_PATH
    }
    if dictionary:
        new_dictionary.update(dictionary)
    return render_to_string(template_name, new_dictionary, context_instance)
