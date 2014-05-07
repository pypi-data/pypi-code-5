from __future__ import absolute_import

from django.core.mail import send_mail
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from classymail.transports.base import BaseTransport

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class DjangoTransport(BaseTransport):
    def send_mail(self, subject, from_email, recipients, message='', html_message='', **kwargs):
        if not html_message:
            # either we're gonna send a blank email or a plain text message
            send_mail(subject, message, from_email, recipient_list=recipients,
                      fail_silently=kwargs.pop('fail_silently', False))
        else:
            email = EmailMultiAlternatives(subject, message, from_email, recipients)
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=kwargs.pop('fail_silently', False))
