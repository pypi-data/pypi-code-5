from classymail import settings
from classymail.rendering.django import DjangoRenderer
from classymail.transports.django import DjangoTransport

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class BaseMessage(object):
    from_email = None
    subject = ''
    template = ''
    type = 'html'

    def get_subject(self):
        return self.subject

    def get_template(self):
        return self.template

    def send(self, recipients, from_email=None, send_context=None):
        context = self.get_base_context()
        if send_context:
            context.update(send_context)

        from_email = from_email or self.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        if not from_email:
            # TODO: parse from_email?
            raise ValueError('from_email may not be empty!')

        message = self.get_render_engine().render(self.get_template(), context=context)

        # TODO: if async, then send async, else send sync
        self.get_transport().send_mail(self.get_subject(), message, from_email, recipients)

    def get_transport(self):
        # TODO: return any transport needed
        return DjangoTransport()

    def get_base_context(self):
        return {}

    def get_render_engine(self):
        return DjangoRenderer()