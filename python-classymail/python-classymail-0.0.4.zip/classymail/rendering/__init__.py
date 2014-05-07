__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'


class BaseRenderer(object):
    def render(self, template, context=None):
        """
        Note: subclasses should return '' if template is blank.
        """
        raise NotImplementedError()