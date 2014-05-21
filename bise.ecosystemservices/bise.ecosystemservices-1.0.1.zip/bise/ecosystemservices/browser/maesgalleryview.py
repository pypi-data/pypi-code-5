from Acquisition import aq_inner
from five import grok
from zope.interface import Interface

grok.templatedir('templates')


class MAESGalleryView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')

    def get_studies(self):
        context = aq_inner(self.context)
        studies = context.getFolderContents({'portal_type': 'Study'},
            full_objects=True)
        ret = []
        for study in studies:
            data = {}
            data['item'] = study
            ret.append(data)

        return ret