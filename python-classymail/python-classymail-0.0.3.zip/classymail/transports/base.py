__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class BaseTransport(object):
    def send_mail(self, subject, message, from_email, recipients, **kwargs):
        raise NotImplementedError()