# coding=utf-8

from os.path import basename
from smtplib import SMTPException

from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives


def send_email(addr_from, addr_to, subject, template, context, attachments=None, reply_to=None):
    from email_helper.models import Email

    # Allow for a single address to be passed in.
    if not hasattr(addr_to, '__iter__'):
        addr_to = [addr_to]

    body = loader.get_template(template).render(Context(context))
    alternatives_parts = [(body, 'text/html')]

    # Load attachments and create name/data tuples.
    attachments_parts = []
    for attachment in attachments or []:
        # Attachments can be pairs of name/data, or filesystem paths.
        if not hasattr(attachment, '__iter__'):
            with open(attachment, 'rb') as f:
                attachments_parts.append((basename(attachment), f.read()))
        else:
            attachments_parts.append(attachment)

    headers = reply_to and {'Reply-To': reply_to}

    msg = EmailMultiAlternatives(subject=subject, body='None', from_email=addr_from, to=addr_to, alternatives=alternatives_parts, attachments=attachments_parts, headers=headers)

    try:
        msg.send()
    except SMTPException as ex:
        status = unicode(ex)
    else:
        status = u'OK'

    Email.objects.create(whom=u', '.join(addr_to), subject=subject, body=body, status=status)
