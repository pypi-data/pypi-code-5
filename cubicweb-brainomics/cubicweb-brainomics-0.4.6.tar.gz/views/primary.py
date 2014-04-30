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

"""cubicweb-suivimp views/forms/actions/components for web ui"""
from logilab.mtconverter import xml_escape
from cubicweb.selectors import is_instance
from cubicweb.web.views.primary import PrimaryView

from cubes.brainomics.entities import MEASURES


###############################################################################
### ABSTRACT PRIMARY VIEW #####################################################
###############################################################################
class BrainomicsPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__
    __abstract__ = True

    def iterate_attributes(self, entity):
        return []

    def iterate_data(self, entity):
        return []

    def _build_data(self, data, rql, label):
        rset = self._cw.execute(rql)
        if len(rset):
            url = self._cw.build_url(rql=rql)
            ahref = u'<a href="%s">%s</a>' % (url, self._cw._('See all'))
            data.append((label, (len(rset), ahref)))
        return data

    def display_main_col(self, entity):
        pass

    def display_additional_header(self, entity):
        pass

    def display_header(self, entity):
        w = self.w
        w(u'<div class="well">')
        w(u'<div class="page-header">')
        w(u'<h2>%s</h2>' % xml_escape(entity.dc_title()))
        w(u'</div>')
        w(u'<dl class="dl-horizontal">')
        for label, attribute in self.iterate_attributes(entity):
            if attribute:
                w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._(label), attribute))
        w(u'</dl>')
        # Additional header
        self.display_additional_header(entity)
        # Data
        self.display_data_table(entity)
        w(u'</div>')

    def display_data_table(self, entity):
        w = self.w
        table_data = self.iterate_data(entity)
        if not table_data:
            return
        w(u'<h3>%s</h3>' % self._cw._('Data overview'))
        w(u'<table class="table table-striped table-bordered table-condensed">')
        for label, data in table_data:
            w(u'<tr>')
            w(u'<th>%s</th>' % self._cw._(label))
            for d in data:
                w(u'<th>%s</th>' % d)
            w(u'</tr>')
        w(u'</table>')

    def call(self, rset=None):
        entity = self.cw_rset.get_entity(0,0)
        w = self.w
        # Tabblables
        w(u'<div class="tab-content">')
        # Mainn table
        w(u'<div class="tab-pane active" id="entity-mainview">')
        # Header
        self.display_header(entity)
        # Main col
        w(u'<div class="row-fluid">')
        self.display_main_col(entity)
        w(u'</div>')
        # Close table
        w(u'</div>')
        # Add other tables
        if 'ctx-entity-tabs' in self._cw.vreg:
            tabs = self._cw.vreg['ctx-entity-tabs'].possible_objects(self._cw, rset=self.cw_rset)
            for tab in tabs:
                tab.render(self.w)
        w(u'</div>')


###############################################################################
### SUBJECT ###################################################################
###############################################################################
class SubjectPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Subject')

    def iterate_attributes(self, entity):
        return [(self._cw._('Age'), entity.display_age_for_assessments()),
                (self._cw._('Handedness'), entity.handedness),
                (self._cw._('Gender'), entity.gender),]

    def display_additional_header(self, entity):
        scores = self._cw.execute('Any X WHERE S related_infos X, S eid %(e)s', {'e': entity.eid})
        if scores:
            self.w(u'<h3>%s</h3>' % self._cw._('Scores'))
            self.wview('list', scores)

    def iterate_data(self, entity):
        data = []
        for measure in MEASURES:
            rql = 'Any X WHERE X is %s, X concerns S, S eid %s' % (measure, entity.eid)
            data = self._build_data(data, rql, self._cw._(measure))
        return data

    def display_main_col(self, entity):
        self.w(u'<div class="span6">')
        # Detailled assessments
        rset = self._cw.execute('Any X WHERE S concerned_by X, S eid %(e)s', {'e': entity.eid})
        if rset:
            self.w(u'<h3>%s</h3>' % self._cw._('Detailed Assessments'))
            self.wview('list', rset=rset)
        self.w(u'</div>')
        self.w(u'<div class="span5">')
        # Related external resources
        rset = self._cw.execute('Any E WHERE X external_resources E, S concerned_by X, S eid %(e)s, '
                                'NOT EXISTS(X generates M)', {'e': entity.eid})
        if rset:
            self.w(u'<h3>%s</h3>' % self._cw._('External Resources'))
            self.wview('list', rset=rset)
        self.w(u'</div>')


############################################################################
### STUDY ##################################################################
############################################################################
class StudyPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Study')

    def iterate_attributes(self, entity):
        return [(self._cw._('Name'), entity.name),
                (self._cw._('Description'), entity.description),
                (self._cw._('Keywords'), entity.keywords),
                (self._cw._('Themes'), ', '.join([t.dc_title() for t in entity.themes]))]

    def iterate_data(self, entity):
        data = []
        # Subjects
        rql = 'Any X WHERE X related_studies S, S eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Subjects'))
        # Measures
        rset = self._cw.execute('Any M, COUNT(X) GROUPBY S, M WHERE X related_study S, '
                                'S eid %s, X is E, E name M' % entity.eid)
        for label, count in rset:
            rql='Any X WHERE X is %s, X related_study S, S eid %s' % (label, entity.eid)
            data = self._build_data(data, rql, self._cw._(label))
        return data


###############################################################################
### INVESTIGATOR ##############################################################
###############################################################################
class InvestigatorPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Investigator')

    def iterate_attributes(self, entity):
        return [(self._cw._('Firstname'), entity.firstname),
                (self._cw._('Lastname'), entity.lastname),
                (self._cw._('Title'), entity.title),
                (self._cw._('Institution'), entity.institution),
                (self._cw._('Department'), entity.department),]

    def display_main_col(self, entity):
        # Detailled assessments
        # XXX Direct link to the measures/runs ?
        self.w(u'<h3>%s</h3>' % self._cw._('Assessments conducted by this investigator'))
        rset = self._cw.execute('Any A WHERE A conducted_by X, X eid %(e)s', {'e': entity.eid})
        if rset:
            self.wview('list', rset)


############################################################################
### CENTER #################################################################
############################################################################
class CenterPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Center')

    def iterate_attributes(self, entity):
        return [(self._cw._('Identifier'), entity.identifier),
                (self._cw._('Department'), entity.department),
                (self._cw._('City'), entity.city),
                (self._cw._('Country'), entity.country),]

    def iterate_data(self, entity):
        data = []
        # Subjects
        rql = 'DISTINCT Any S WHERE S is Subject, X holds A, S concerned_by A, X eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Subjects'))
        # Assessments
        rql = 'DISTINCT Any A WHERE X holds A, X eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Assessments'))
        return data

    def display_main_col(self, entity):
        # Devices
        rset = self._cw.execute('Any S WHERE S is Device, '
                                'S hosted_by X, X eid %(e)s', {'e': entity.eid})
        if rset:
            self.w(u'<h3>Devices</h3>')
            self.wview('list', rset=rset)


############################################################################
### DEVICE #################################################################
############################################################################
class DevicePrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Device')

    def iterate_attributes(self, entity):
        center = entity.hosted_by[0]
        center = u'<a href="%s">%s</a>' % (center.absolute_url(), center.dc_title())
        return [(self._cw._('Name'), entity.name),
                (self._cw._('Manufacturer'), entity.manufacturer),
                (self._cw._('Model'), entity.model),
                (self._cw._('Hosted by'), center),]

    def iterate_data(self, entity):
        data = []
        rql = 'DISTINCT Any S WHERE S uses_device X, X eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Generated measures'))
        return data


############################################################################
### ASSESSMENT #############################################################
############################################################################
class AssessmentPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Assessment')

    def iterate_attributes(self, entity):
        subject = entity.reverse_concerned_by[0]
        subject = u'<a href="%s">%s</a>' % (subject.absolute_url(), subject.dc_title())
        return [(self._cw._('Identifier'), entity.identifier),
                (self._cw._('Protocol'), entity.protocol),
                (self._cw._('Date'), entity.datetime),
                (self._cw._('Subject'), subject),
                (self._cw._('Study'), entity.related_study[0].view('outofcontext')),
                (self._cw._('Center'), entity.reverse_holds[0].view('outofcontext')),
                ]

    def iterate_data(self, entity):
        data = []
        # Generated
        rset = self._cw.execute('Any M, COUNT(S) GROUPBY M WHERE X generates S, X eid %s, '
                                'S is E, E name M' % entity.eid)
        for m, count in rset:
            rql = 'Any S WHERE X generates S, S is %s, X eid %s' % (m, entity.eid)
            data = self._build_data(data, rql, self._cw._('Generated %(s)s' % {'s': m}))
        # Used
        rset = self._cw.execute('Any M, COUNT(S) GROUPBY M WHERE X uses S, X eid %s, '
                                'S is E, E name M' % entity.eid)
        for m, count in rset:
            rql = 'Any S WHERE X uses S, S is %s, X eid %s' % (m, entity.eid)
            data = self._build_data(data, rql, self._cw._('Used %(s)s' % {'s': m}))
        return data


###############################################################################
### SCOREDEF ##################################################################
###############################################################################
class ScoreDefinitionPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('ScoreDefinition')

    def iterate_attributes(self, entity):
        return [(self._cw._('Name'), entity.name),
                (self._cw._('Category'), entity.category),
                (self._cw._('Type'), entity.type),
                (self._cw._('Unit'), entity.unit),
                (self._cw._('Possible values'), entity.possible_values)
                ]

    def display_main_col(self, entity):
        # Scores
        w = self.w
        rset = self._cw.execute('Any S,V,T,DA WHERE S is ScoreValue, S value V, S text T, '
                                'S datetime DA, S definition D, D eid %(e)s', {'e': entity.eid})
        if not rset:
            return
        w(u'<table class="table table-striped table-bordered table-condensed">')
        w(u'<tr><th>%s</th><th>%s</th><th>%s</th></tr>'
          % (self._cw._('Subject'), self._cw._('value'), self._cw._('datetime')))
        # Warm subjects
        score = rset.get_entity(0, 0)
        if score.reverse_related_infos:
            subjects_rset = self._cw.execute('Any SB, S, I WHERE S is ScoreValue, '
                                             'SB related_infos S, SB identifier I, '
                                             'S definition D, D eid %(e)s', {'e': entity.eid})
        else:
            # Measure/concerns
            subjects_rset = self._cw.execute('Any SB, S, I WHERE S is ScoreValue, '
                                             'S measure M, M concerns SB, SB identifier I, '
                                             'S definition D, D eid %(e)s', {'e': entity.eid})
        subjects = {}
        for ind, e in enumerate(subjects_rset.entities()):
            subjects[subjects_rset[ind][1]] = e
        # Plot results
        for ind in range(len(rset)):
            score = rset.get_entity(ind, 0)
            subj = subjects[score.eid]
            if subj:
                subject = u'<a href="%s">%s</a>' % (subj.absolute_url(), subj.identifier)
            else:
                subject = u'<unknown - error>'
            w(u'<tr><th>%s</th><th>%s</th><th>%s</th></tr>'
              % (subject, score.complete_value, score.datetime or '-'))
        w(u'</table>')


###############################################################################
### GENERIC TEST RUN ##########################################################
###############################################################################
class GenericTestRunPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('GenericTestRun')

    def iterate_attributes(self, entity):
        test = entity.instance_of[0]
        test = u'<a href="%s">%s</a>' % (test.absolute_url(), test.dc_title())
        subject = entity.concerns[0]
        subject = u'<a href="%s">%s</a>' % (subject.absolute_url(), subject.dc_title())
        return [(self._cw._('Date'), entity.datetime),
                (self._cw._('Instance of'), test),
                (self._cw._('Subject'), subject),]

    def display_main_col(self, entity):
        w = self.w
        # Scores
        self.w(u'<div class="span9">')
        rset = self._cw.execute('Any SD, S WHERE QR is GenericTestRun, QR eid %(e)s, '
                                'S measure QR, S definition SD, S value V, S text T',
                                {'e': entity.eid})
        w(u'<table class="table table-striped table-bordered table-condensed">')
        w(u'<tr>')
        for label in ('score', 'text/value'):
                        w(u'<th>%s</th>' % self._cw._(label))
        w(u'</tr>')
        for ind, scoredef in enumerate(rset.entities()):
            w(u'<tr>')
            w(u'<th><a href="%s">%s</a></th>' % (scoredef.absolute_url(), scoredef.dc_title()))
            w(u'<th>%s</th>' % (rset.get_entity(ind, 1).complete_value))
            w(u'</tr>')
        w(u'</table>')
        self.w(u'</div>')
        # Related external resources
        self.w(u'<div class="span3">')
        rset = self._cw.execute('(Any E WHERE X external_resources E, X eid %(e)s) '
                                'UNION (Any E WHERE A generates X, A external_resources E, X eid %(e)s)',
                                {'e': entity.eid})
        if rset:
            w(u'<h3>%s</h3>' % self._cw._('External Resources'))
            self.wview('list', rset=rset)
        self.w(u'</div>')


###############################################################################
### GENERIC TEST ##############################################################
###############################################################################
class GenericTestPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('GenericTest')

    def iterate_attributes(self, entity):
        return [(self._cw._('Identifier'), entity.identifier),
                (self._cw._('Name'), entity.name),
                (self._cw._('Type'), entity.type),
                (self._cw._('Version'), entity.version),
                (self._cw._('Language'), entity.language),
                (self._cw._('Note'), entity.note),]

    def iterate_data(self, entity):
        data = []
        rql = 'Any S WHERE S instance_of X, X eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Test runs'))
        return data


###############################################################################
### EXTERNAL RESOURCE #########################################################
###############################################################################
class ExternalResourcePrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('ExternalResource')

    def iterate_attributes(self, entity):
        study = entity.related_study
        study = u'<a href="%s">%s</a>' % (study[0].absolute_url(), study[0].dc_title()) if study else u''
        return [(self._cw._('Name'), entity.name),
                (self._cw._('Filepath'), entity.filepath),
                (self._cw._('Study'), study),
                ]


###############################################################################
### QUESTIONNAIRERUN ##########################################################
###############################################################################
class QuestionnaireRunPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('QuestionnaireRun')

    def iterate_attributes(self, entity):
        questionnaire = entity.instance_of[0]
        questionnaire = u'<a href="%s">%s</a>' % (questionnaire.absolute_url(), questionnaire.dc_title())
        subject = entity.concerns[0]
        subject = u'<a href="%s">%s</a>' % (subject.absolute_url(), subject.dc_title())
        assessment = entity.reverse_generates[0]
        assessment = u'<a href="%s">%s</a>' % (assessment.absolute_url(), assessment.dc_title())
        return [(self._cw._('Date'), entity.datetime),
                (self._cw._('Instance of'), questionnaire),
                (self._cw._('Subject'), subject),
                (self._cw._('Assessment'), assessment),
                ]


    def display_additional_header(self, entity):
        w = self.w
        # Scores and External resources
        rset = self._cw.execute('Any X WHERE X is ScoreValue, X measure Q, Q eid %(q)s',
                                {'q': entity.eid})
        if rset:
            w(u'<h3>%s</h3>' % self._cw._('Additional scores'))
            self.wview('list', rset=rset)
        rset = self._cw.execute('Any X WHERE X is ExternalResource, Q external_resources X, Q eid %(q)s',
                                {'q': entity.eid})
        if rset:
            w(u'<h3>%s</h3>' % self._cw._('Additional resources'))
            self.wview('list', rset=rset)

    def display_main_col(self, entity):
        w = self.w
        # Results file
        w(entity.view('results-view'))
        # Answers
        w(u'<h3>%s</h3>' % self._cw._('Answers'))
        rset = self._cw.execute('Any Q, A, AV, AD ORDERBY QP '
                                'WHERE QR is QuestionnaireRun, QR eid %(e)s, '
                                'A questionnaire_run QR, A question Q, '
                                'A value AV, A datetime AD, '
                                'Q identifier QI, Q position QP, Q text QT, '
                                'Q type QTY, Q possible_answers QPA',
                                {'e': entity.eid})
        w(u'<table class="table table-striped table-bordered table-condensed">')
        w(u'<tr>')
        for label in ('question', 'text', 'value', 'datetime'):
            w(u'<th>%s</th>' % self._cw._(label))
        w(u'</tr>')
        for ind, question in enumerate(rset.entities()):
            w(u'<tr>')
            w(u'<th><a href="%s">%s</a></th>' % (question.absolute_url(), question.identifier))
            w(u'<th>%s</th>' % question.text)
            answer = rset.get_entity(ind, 1)
            w(u'<th>%s</th>' % answer.computed_value)
            w(u'<th>%s</th>' % (answer.datetime or self._cw._(u'unknown')))
            w(u'</tr>')
        w(u'</table>')


###############################################################################
### QUESTIONNAIRE #############################################################
###############################################################################
class QuestionnairePrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Questionnaire')

    def iterate_attributes(self, entity):
        return [(self._cw._('Name'), entity.name),
                (self._cw._('Type'), entity.type),
                (self._cw._('Version'), entity.version),
                (self._cw._('Language'), entity.language),
                (self._cw._('Note'), entity.note),
                ]

    def iterate_data(self, entity):
        data = []
        rql = 'Any S WHERE S is QuestionnaireRun, S instance_of X, X eid %s' % entity.eid
        data = self._build_data(data, rql, self._cw._('Related runs'))
        return data

    def display_main_col(self, entity):
        # Results file
        self.w(entity.view('results-view'))
        # Questions
        w = self.w
        rset = self._cw.execute('Any Q, QI, QP, QT, QTY, QPA ORDERBY QP '
                                'WHERE QR is Questionnaire, QR eid %(e)s, '
                                'Q questionnaire QR, '
                                'Q identifier QI, Q position QP, Q text QT, '
                                'Q type QTY, Q possible_answers QPA',
                                {'e': entity.eid})
        w(u'<table class="table table-striped table-bordered table-condensed">')
        w(u'<tr>')
        for label in ('question', 'text', 'type', 'possible_answers', 'Answers'):
            w(u'<th>%s</th>' % self._cw._(label))
        w(u'</tr>')
        for question in rset.entities():
            w(u'<tr>')
            possible_answers = question.displayable_possible_answers
            for value in (question.identifier, question.text, question.type, possible_answers):
                w(u'<th>%s</th>' % value)
            w(u'<th><a href="%s">%s</a></th>' % (question.absolute_url(), self._cw._('See detailled question')))
            w(u'</tr>')
        w(u'</table>')


###############################################################################
### QUESTION ##################################################################
###############################################################################
class QuestionPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Question')

    def iterate_attributes(self, entity):
        questionnaire = entity.questionnaire[0]
        questionnaire = u'<a href="%s">%s</a>' % (questionnaire.absolute_url(), questionnaire.dc_title())
        return [(self._cw._('Questionnaire'), questionnaire),
                (self._cw._('Position'), entity.position),
                (self._cw._('Text'), entity.text),
                (self._cw._('Type'), entity.type),
                (self._cw._('Possible answers'), entity.possible_answers),
                ]

    def display_main_col(self, entity):
        # Answers
        w = self.w
        rset = self._cw.execute('Any A, AQ, S, Q, AV, AD, AI, I, QT, QPA WHERE A is Answer, '
                                'A question Q, Q eid %(e)s, Q type QT, Q possible_answers QPA, '
                                'A value AV, A datetime AD, AQ identifier AI, '
                                'A questionnaire_run AQ, AQ concerns S, S identifier I',
                                {'e': entity.eid})
        w(u'<table class="table table-striped table-bordered table-condensed">')
        w(u'<tr>')
        for label in ('answer',  'value', 'datetime'):
            w(u'<th>%s</th>' % self._cw._(label))
        w(u'</tr>')
        for ind, answer in enumerate(rset.entities()):
            # XXX WARM CACHE ?
            qrun = rset.get_entity(ind, 1)
            subject = rset.get_entity(ind, 2)
            question = rset.get_entity(ind, 3)
            w(u'<tr>')
            w(u'<th><a href="%s">%s</a></th>' % (answer.absolute_url(), answer.dc_title()))
            w(u'<th>%s</th>' % answer.computed_value)
            w(u'<th>%s</th>' % (answer.datetime or self._cw._(u'unknown')))
            w(u'</tr>')
        w(u'</table>')


###############################################################################
### SCAN ######################################################################
###############################################################################
class ScanPrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Scan')

    def iterate_attributes(self, entity):
        subject = entity.concerns[0]
        subject = u'<a href="%s">%s</a>' % (subject.absolute_url(), subject.dc_title())
        device = entity.uses_device
        if entity.uses_device:
            device = u'<a href="%s">%s</a>' % (device[0].absolute_url(), device[0].dc_title())
        else:
            device = None
        assessment = entity.reverse_generates[0]
        assessment = u'<a href="%s">%s</a>' % (assessment.absolute_url(), assessment.dc_title())
        return [(self._cw._('Identifier'), entity.identifier),
                (self._cw._('Label'), entity.label),
                (self._cw._('Type'), entity.type),
                (self._cw._('Format'), entity.format),
                (self._cw._('Position in acquisition'), entity.position_acquisition),
                (self._cw._('Subject'), subject),
                (self._cw._('Device'), device),
                (self._cw._('Assessment'), assessment),
                ]

    def display_header(self, entity):
        w = self.w
        w(u'<div class="well">')
        w(u'<div class="page-header">')
        w(u'<h2>%s</h2>' % xml_escape(entity.dc_title()))
        w(u'</div>')
        w(u'<dl class="dl-horizontal">')
        for label, attribute in self.iterate_attributes(entity):
            if attribute:
                w(u'<dt>%s</dt><dd>%s</dd>' % (self._cw._(label), attribute))
        # Add data info
        data = entity.has_data
        if data:
            data[0].view('scan-data-view', w=w)
        w(u'</dl>')
        # Additional header
        self.display_additional_header(entity)
        # Data
        self.display_data_table(entity)
        w(u'</div>')

    def display_main_col(self, entity):
        # Results file
        self.w(entity.view('results-view'))
        # Related external resources
        rset = self._cw.execute('(Any E WHERE X external_resources E, X eid %(e)s) '
                                'UNION (Any E WHERE A generates X, A external_resources E, X eid %(e)s)',
                                {'e': entity.eid})
        if rset:
            self.w(u'<h3>%s</h3>' % self._cw._('External Resources'))
            self.wview('list', rset=rset)


###############################################################################
### GENOMIC MEASURE ###########################################################
###############################################################################
class GenomicMeasurePrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('GenomicMeasure')

    def iterate_attributes(self, entity):
        subject = entity.concerns[0]
        subject = u'<a href="%s">%s</a>' % (subject.absolute_url(), subject.dc_title())
        fields = [(self._cw._('Type'), entity.type),
                  (self._cw._('Format'), entity.format),
                  (self._cw._('File path'), entity.filepath),
                  (self._cw._('Chip S/N'), entity.formatted_chip_serialnum),
                  (self._cw._('Subject'), subject),
                  (self._cw._('Study'), entity.related_study[0].view('outofcontext'))]
        if entity.platform:
            fields.append((self._cw._('Platform'), entity.platform[0].view('outofcontext')))
        return fields

    def display_main_col(self, entity):
        self.w(entity.view('results-view'))
        cgh_results = self._cw.execute('Any R WHERE R is CghResult, '
                                       'R related_measure X, X eid %(e)s',
                                       {'e': entity.eid})
        mutation_results = self._cw.execute('Any R WHERE R is Mutation, '
                                            'R related_measure X, X eid %(e)s',
                                            {'e': entity.eid})
        if cgh_results or mutation_results:
            self.w(u'<div class="span3">')
            if cgh_results:
                self.w(u'<h3>%s</h3>' % self._cw._('CGH results'))
                self.wview('cgh-table-view', rset=cgh_results)
            if mutation_results:
                self.w(u'<h3>%s</h3>' % self._cw._('Sequencing results'))
                self.wview('mutation-table-view', rset=mutation_results)
            self.w(u'</div>')


###############################################################################
### GENE ######################################################################
###############################################################################
class GenePrimaryView(BrainomicsPrimaryView):
    __select__ = BrainomicsPrimaryView.__select__ & is_instance('Gene')

    def iterate_attributes(self, entity):
        fields = [(self._cw._('Identifier'), entity.gene_id),
                  (self._cw._('Start position'), entity.start_position),
                  (self._cw._('Stop position'), entity.stop_position),
                  (self._cw._('Chromosome'), entity.chromosome[0].view('outofcontext'))]
        return fields

    def display_main_col(self, entity):
        cgh_results = self._cw.execute('Any R WHERE R is CghResult, '
                                       'R related_gene X, X eid %(e)s',
                                       {'e': entity.eid})
        mutation_results = self._cw.execute('Any R WHERE R is Mutation, '
                                            'R related_gene X, X eid %(e)s',
                                            {'e': entity.eid})
        if cgh_results or mutation_results:
            self.w(u'<div class="span3">')
            if cgh_results:
                self.w(u'<h3>%s</h3>' % self._cw._('CGH results'))
                self.wview('gene-cgh-table-view', rset=cgh_results)
            if mutation_results:
                self.w(u'<h3>%s</h3>' % self._cw._('Sequencing results'))
                self.wview('gene-mutation-table-view', rset=mutation_results)
            self.w(u'</div>')
