# -*- coding: utf8 -*-

import json
from plone.app.layout.viewlets import ViewletBase
from zope.component import getAdapters
from collective.jsconfiguration.interfaces import IJSONDataProvider
from collective.jsconfiguration.interfaces import IJSObjectDataProvider
from collective.jsconfiguration.interfaces import IDOMDataProvider
from zope.component.interfaces import ComponentLookupError


JS_SCRIPT = """<script type="text/javascript">
{{placeholder}}
{{var_assignment}}
</script>
"""

VAR_DEF = """if (typeof {{name}}==='undefined') {
    {{name}} = {};
}
"""

VAR_ASSIGN = '{{name}} = {{object}};'


class JSConfigurationViewlet(ViewletBase):
    """Display JavaScript configuration (pure JavaScript, JSON or HTML data attributes) in the page"""

    def update(self):
        super(JSConfigurationViewlet, self).update()

    def json_data(self):
        """Load all IJSONDataProvider providers"""
        json_providers = getAdapters((self.context, self.request, self.view), IJSONDataProvider)
        results = []
        for name, provider in json_providers:
            results.append({'name': name or None,
                            'data': json.dumps(provider())})
        return results

    def js_data(self):
        """Load all IJSObjectDataProvider providers"""
        js_providers = getAdapters((self.context, self.request, self.view), IJSObjectDataProvider)
        results = []
        for name, provider in js_providers:
            if not name:
                raise ComponentLookupError('IJSObjectDataProvider must be a named adapter')
            names = name.split('.')
            var_defs = ''
            parts = []
            for n in names[:-1]:
                parts.append(n)
                var_defs += VAR_DEF.replace('{{name}}', '.'.join(parts))
            parts.append(names[-1])
            code = JS_SCRIPT.replace('{{placeholder}}', var_defs)
            code = code.replace('{{var_assignment}}',
                                VAR_ASSIGN.replace('{{name}}',
                                                   '.'.join(parts)).replace('{{object}}',
                                                                            json.dumps(provider())))
            results.append(code)
        return results

    def dom_data(self):
        """Load all IDOMDataProvider providers"""
        dom_providers = getAdapters((self.context, self.request, self.view), IDOMDataProvider)
        results = []
        for name, provider in dom_providers:
            results.append({'name': name or None,
                            'data': provider()})
        return results
