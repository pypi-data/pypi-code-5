# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2013 CEA (Saclay, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web.views.baseviews import ListView


###############################################################################
### LIST VIEW #################################################################
###############################################################################
class BrainomicsListView(ListView):

    def call(self, klass=None, title=None, subvid=None, listid=None, **kwargs):
        super(BrainomicsListView, self).call(klass="unstyled stripped",
                                             title=title, subvid=subvid,
                                             listid=listid, **kwargs)


###############################################################################
### CARD VIEW #################################################################
###############################################################################
class BrainomicsCardDocumentation(EntityView):
    __regid__ = 'documentation_card'
    __select__ = EntityView.__select__ & is_instance('Card')

    def call(self, rset=None, **kwargs):
        rset = rset or self.cw_rset
        w = self.w
        w(u'<div>')
        for entity in rset.entities():
            w(u'<h2>%s</h2>' % xml_escape(entity.title))
            if entity.synopsis:
                w(u'<blockquote><p>%s</p></blockquote>' % xml_escape(entity.synopsis))
            if entity.content:
                w(entity.content)
        w(u'</div>')


###############################################################################
### RESOURCES VIEW ############################################################
###############################################################################
class BrainomicsResultFile(EntityView):
    __regid__ = 'results-view'
    __select__ = EntityView.__select__ & is_instance('Questionnaire', 'QuestionnaireRun',
                                                     'GenomicMeasure', 'Scan')

    def entity_call(self, entity):
        # Display results file
        w = self.w
        rset = self._cw.execute('Any F WHERE X results_file F, X eid %(e)s',
                                {'e': entity.eid})
        if rset:
            w(u'<h3>%s</h3>' % self._cw._('Results file'))
            self.wview('list', rset=rset)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (BrainomicsListView,))
    vreg.register_and_replace(BrainomicsListView, ListView)

