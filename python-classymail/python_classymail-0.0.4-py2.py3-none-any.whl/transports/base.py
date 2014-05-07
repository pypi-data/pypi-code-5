__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class BaseTransport(object):
    def send_mail(self, subject, from_email, recipients, message='', html_message='', **kwargs):
        raise NotImplementedError()