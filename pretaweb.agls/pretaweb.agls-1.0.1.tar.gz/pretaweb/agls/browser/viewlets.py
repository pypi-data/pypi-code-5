from Acquisition import aq_inner

from zope.component import getUtility

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import shasattr

from plone.registry.interfaces import IRegistry
from plone.app.layout.viewlets.common import DublinCoreViewlet

from pretaweb.agls.config import AGLS_SCHEME


class AGLSViewlet(DublinCoreViewlet):
    index = ViewPageTemplateFile('templates/agls.pt')
    
    def update(self):
        super(AGLSViewlet, self).update()
        
        # DC tags are switched off in Plone control panel
        if not self.metatags:
            return
        
        # map dublin core meta tags
        dc = {}
        for tag in self.metatags:
            dc[tag[0]] = tag[1]
        
        context = aq_inner(self.context)
        agls_tags = []

        agls = context.unrestrictedTraverse("@@agls")
        value = agls.Title() or dc.get('DC.Title', '') or context.Title()
        agls_tags.append({
            'name': u'DCTERMS.title',
            'content': safe_unicode(agls.Title()),
            'scheme': AGLS_SCHEME['DCTERMS.title']
        })
        
        # AGLS Description
        value = agls.Description() or dc.get('DC.description', '')
        agls_tags.append({
            'name': u'DCTERMS.description',
            'content': safe_unicode(value),
            'scheme': AGLS_SCHEME['DCTERMS.description']
        })
        agls_tags.append({
            'name': u'description',
            'content': safe_unicode(value),
            'scheme': AGLS_SCHEME['description']
        })
        
        # AGLS Date
        agls_tags.append({
            'name': u'DCTERMS.created',
            'content': agls.Created(),
            'scheme': AGLS_SCHEME['DCTERMS.created']
        })
        
        agls_tags.append({
            'name': u'DCTERMS.creator',
            'content': safe_unicode(agls.Creator() or dc.get('DC.creator', '')),
            'scheme': AGLS_SCHEME['DCTERMS.creator']
        })

        value = agls.Subject() or '; '.join(dc.get('DC.subject', '').split(', '))
        agls_tags.append({
            'name': u'DCTERMS.subject',
            'content': safe_unicode(value),
            'scheme': AGLS_SCHEME['DCTERMS.subject']
        })
        
        # AGLS Type
        agls_tags.append({
            'name': u'DCTERMS.type',
            'content': safe_unicode(agls.Type()),
            'scheme': AGLS_SCHEME['DCTERMS.type']
        })
        
        # AGLS Identifier
        agls_tags.append({
            'name': u'DCTERMS.identifier',
            'content': agls.Identifier(),
            'scheme': AGLS_SCHEME['DCTERMS.identifier']
        })
        
        # copy over keywords tag
        if 'keywords' in dc:
            agls_tags.append({
                'name': u'keywords',
                'content': safe_unicode(dc['keywords']),
                'scheme': None
            })
        
        # AGLS Publisher
        agls_tags.append({
            'name': u'DCTERMS.publisher',
            'content': safe_unicode(agls.Publisher() or dc.get('DC.creator', '') or context.Creator()),
            'scheme': AGLS_SCHEME['DCTERMS.publisher']
        })

        # AGLS Format
        agls_tags.append({
            'name': u'DCTERMS.format',
            'content': safe_unicode(agls.Format() or dc.get('DC.format', '')),
            'scheme': AGLS_SCHEME['DCTERMS.format']
        })

        self.metatags = tuple(agls_tags)
