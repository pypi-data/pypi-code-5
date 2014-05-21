from Acquisition import aq_inner
from five import grok
from zope.interface import Interface

grok.templatedir('templates')


class AtlasView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')

    def get_ecosystems(self):
        context = aq_inner(self.context)
        ecosystems = context.getFolderContents({'portal_type': 'Ecosystem'},
            full_objects=True)
        ret = []
        for ecosystem in ecosystems:
            data = {}
            data['item'] = ecosystem
            data['services'] = ecosystem.getFolderContents(
                {'portal_type': 'Service'},
                full_objects=True,
            )
            ret.append(data)

        return ret
