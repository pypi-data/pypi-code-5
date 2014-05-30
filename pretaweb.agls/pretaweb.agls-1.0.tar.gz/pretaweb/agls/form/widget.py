from AccessControl import ClassSecurityInfo

from zope.interface import implementer
from zope.component import adapter
from zope.i18n import translate
import zope.schema.interfaces

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Widget import KeywordWidget

from z3c.form.interfaces import IFormLayer, IFieldWidget
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget

from collective.z3cform.keywordwidget import widget as z3cwidget
from collective.z3cform.keywordwidget.interfaces import IKeywordCollection


class MultipleIndexKeywordWidget(KeywordWidget):
    _properties = KeywordWidget._properties.copy()
    _properties.update({
        'macro' : "multipleindexkeyword_widget",
        'indexes': () # list of catalog indexes to get existing keywords from
        })

    security = ClassSecurityInfo()

    security.declarePublic('getExistingKeywords')
    def getExistingKeywords(self, context, fieldName, accessor, vocab_source):
        """Returns existing keywords from catalog indexes"""
        if len(self.indexes) == 0:
            return ()
        
        # if enforce then do not add any extra keywords
        allowed, enforce = context.Vocabulary(fieldName)
        result = allowed.values()
        
        if not enforce:
            catalog = getToolByName(context, vocab_source)
            for index in self.indexes:
                result += catalog.uniqueValuesFor(index)
        
        # remove duplicates
        result = [term for term in set(result)]
        result.sort()
        
        return result

class Z3CFormKeywordWidget(z3cwidget.KeywordWidget):
    """Add items attribute, it's set to () in parent class"""
    
    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })
        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                content = translate(
                    term.title, context=self.request, default=term.title)
            items.append(
                {'id':id, 'value':term.token, 'content':content,
                 'selected':selected})
        return items

@adapter(IKeywordCollection, IFormLayer)
@implementer(IFieldWidget)
def Z3CFormKeywordFieldWidget(field, request):
    """ IFieldWidget factory for Z3CFormKeywordWidget 
    """
    return FieldWidget(field, Z3CFormKeywordWidget(request))
