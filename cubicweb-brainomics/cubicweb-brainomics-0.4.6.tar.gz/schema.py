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

"""cubicweb-brainomics schema"""
from cubicweb.schemas.base import CWUser
from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation, String, RichString,
                            Int, Float, Boolean)

from cubes.questionnaire.schema import QuestionnaireRun, Questionnaire, Question
from cubes.neuroimaging.schema import Scan, AnatomicalRegion
from cubes.genomics.schema import GenomicMeasure, ColumnRef
from cubes.medicalexp.schema  import Assessment, ProcessingRun, ScoreDefinition, ScoreValue

from cubes.brainomics import COMMENTED_ENTITIES, WIKI_ENTITIES


# ProcessingRun -> Measure
ProcessingRun.add_relation(SubjectRelation('QuestionnaireRun', cardinality='**'), name='inputs')
ProcessingRun.add_relation(SubjectRelation('Scan', cardinality='**'), name='inputs')
ProcessingRun.add_relation(SubjectRelation('GenomicMeasure', cardinality='**'), name='inputs')

ProcessingRun.add_relation(SubjectRelation('QuestionnaireRun', cardinality='**'), name='outputs')
ProcessingRun.add_relation(SubjectRelation('Scan', cardinality='**'), name='outputs')
ProcessingRun.add_relation(SubjectRelation('GenomicMeasure', cardinality='**'), name='outputs')

# Maesure -> Subject
QuestionnaireRun.add_relation(SubjectRelation(('Subject', 'Group'), cardinality='1*', inlined=True), name='concerns')
Scan.add_relation(SubjectRelation(('Subject', 'Group'), cardinality='1*', inlined=True), name='concerns')
GenomicMeasure.add_relation(SubjectRelation(('Subject', 'Group'), cardinality='1*', inlined=True), name='concerns')

# Assessment -> Measure
Assessment.add_relation(SubjectRelation('QuestionnaireRun', cardinality='**'), name='uses')
Assessment.add_relation(SubjectRelation('Scan', cardinality='**'), name='uses')
Assessment.add_relation(SubjectRelation('GenomicMeasure', cardinality='**'), name='uses')

Assessment.add_relation(SubjectRelation('QuestionnaireRun', cardinality='?*'), name='generates')
Assessment.add_relation(SubjectRelation('Scan', cardinality='?*'), name='generates')
Assessment.add_relation(SubjectRelation('GenomicMeasure', cardinality='?*'), name='generates')

# Score -> Measure
ScoreValue.add_relation(SubjectRelation('QuestionnaireRun', cardinality='?*'), name='measure')
ScoreValue.add_relation(SubjectRelation('Scan', cardinality='?*'), name='measure')
ScoreValue.add_relation(SubjectRelation('GenomicMeasure', cardinality='?*'), name='measure')

# Use for filepath computation
QuestionnaireRun.add_relation(SubjectRelation('Study', cardinality='1*', inlined=True), name='related_study')
Scan.add_relation(SubjectRelation('Study', cardinality='1*', inlined=True), name='related_study')
GenomicMeasure.add_relation(SubjectRelation('Study', cardinality='1*', inlined=True), name='related_study')
QuestionnaireRun.add_relation(SubjectRelation('Study', cardinality='**'), name='other_studies')
Scan.add_relation(SubjectRelation('Study', cardinality='**'), name='other_studies')
GenomicMeasure.add_relation(SubjectRelation('Study', cardinality='**'), name='other_studies')

# Device -> Measure
QuestionnaireRun.add_relation(SubjectRelation('Device', cardinality='?*', inlined=True), name='uses_device')
Scan.add_relation(SubjectRelation('Device', cardinality='?*', inlined=True), name='uses_device')
GenomicMeasure.add_relation(SubjectRelation('Device', cardinality='?*', inlined=True), name='uses_device')

# Measure -> ExternalResources
# Questionnaire may have some specifications files
Questionnaire.add_relation(SubjectRelation('ExternalResource', cardinality='*1'), name='external_resources')
# Some questionnaire run could have specific results files (subject dependant)
QuestionnaireRun.add_relation(SubjectRelation('ExternalResource', cardinality='*1'), name='external_resources')
Scan.add_relation(SubjectRelation('ExternalResource', cardinality='*1'), name='external_resources')
GenomicMeasure.add_relation(SubjectRelation('ExternalResource', cardinality='*1'), name='external_resources')

# Various relations
Questionnaire.add_relation(SubjectRelation('ScoreDefinition', cardinality='*?'), name='definitions')
ScoreDefinition.add_relation(SubjectRelation('Question', cardinality='**'), name='used_by')
AnatomicalRegion.add_relation(SubjectRelation('ScoreValue', cardinality='**'), name='concerned_by')
ColumnRef.add_relation(SubjectRelation('Assessment', cardinality='1*', inlined=True), name='assessment')

# Extra fields for CWUser

CWUser.add_relation(String(maxsize=512, fulltextindexed=True), name='affiliation')
CWUser.add_relation(String(maxsize=512, fulltextindexed=True), name='extra_infos')


# Comments for entities
class comments(RelationDefinition):
    subject = 'Comment'
    object = COMMENTED_ENTITIES

# Links to "Wikis" / Cards
class wiki(RelationDefinition):
    subject = WIKI_ENTITIES
    object = 'Card'
    cardinality = '**'
