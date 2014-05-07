from classymail import settings
from classymail.rendering.django import DjangoRenderer
from classymail.transports.django import DjangoTransport

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class BaseMessage(object):
    from_email = None
    subject = ''
    html_template = ''
    text_template = ''
    type = 'html'

    def get_subject(self):
        return self.subject

    def get_html_template(self):
        return self.html_template

    def send(self, recipients, from_email=None, send_context=None):
        # TODO: if async, then fire async send, else send sync ... move code below to task?
        context = self.get_base_context()
        if send_context:
            context.update(send_context)

        from_email = from_email or self.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        if not from_email:
            # TODO: parse from_email?
            raise ValueError('from_email may not be empty!')

        engine = self.get_render_engine()
        html_message = engine.render(self.get_html_template(), context=context)
        text_message = engine.render(self.get_text_template(), context=context)

        self.get_transport().send_mail(self.get_subject(), from_email, recipients, message=text_message,
                                       html_message=html_message)

    def get_transport(self):
        # TODO: return any transport needed
        return DjangoTransport()

    def get_base_context(self):
        return {}

    def get_render_engine(self):
        return DjangoRenderer()

    def get_text_template(self):
        return self.text_template