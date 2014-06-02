from __future__ import absolute_import
from .utils import dumps_list
from .base_classes import BaseLaTeXContainer


class Math(BaseLaTeXContainer):
    def __init__(self, data=None, inline=False):
        self.inline = inline
        super(Math, self).__init__(data)
    __init__.func_annotations = {}

    def dumps(self):
        if self.inline:
            string = u'$' + dumps_list(self, token=u' ') + u'$'
        else:
            string = u'$$' + dumps_list(self, token=u' ') + u'$$\n'

        super(Math, self).dumps()
        return string
    dumps.func_annotations = {}
