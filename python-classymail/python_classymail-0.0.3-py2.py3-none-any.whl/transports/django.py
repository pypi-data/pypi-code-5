from __future__ import absolute_import

from django.core.mail import send_mail
from classymail.transports.base import BaseTransport

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class DjangoTransport(BaseTransport):
    def send_mail(self, subject, message, from_email, recipients, **kwargs):
        send_mail(subject, message, from_email, recipient_list=recipients,
                  fail_silently=kwargs.pop('fail_silently', False))