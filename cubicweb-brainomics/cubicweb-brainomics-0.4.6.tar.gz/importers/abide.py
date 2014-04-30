# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

import csv
import sys
import os
import os.path as osp
import glob

import nibabel as nb

from cubicweb.dataimport import SQLGenObjectStore as Store

from cubes.brainomics.importers.helpers import get_image_info


SEX = {'1': u'male', '2': u'female'}
HANDEDNESS = {'R': u'right', 'L': u'left', 'Ambi': u'ambidextrous', 'Mixed': u'mixed'}


###############################################################################
### GROUPS AND SCORES #########################################################
###############################################################################
def create_groups_and_categories(session):
    """Create groups and categories"""
    groups = {}
    groups[1] = store.create_entity('Group', identifier=u'abide_autism', name=u'Diagnostic group Autism').eid
    groups[2] = store.create_entity('Group', identifier=u'abide_control', name=u'Diagnostic group Control').eid
    categories = {}
    categories['0'] = store.create_entity('Group', identifier=u'abide_category_control',
                                          name=u'Diagnostic category Control').eid
    categories['1'] = store.create_entity('Group', identifier=u'abide_category_autism',
                                          name=u'Diagnostic category Autism').eid
    categories['2'] = store.create_entity('Group', identifier=u'abide_category_asperger',
                                          name=u'Diagnostic category Aspergers').eid
    categories['3'] = store.create_entity('Group', identifier=u'abide_category_pdd_nos',
                                          name=u'Diagnostic category PDD-NOS').eid
    categories['4'] = store.create_entity('Group', identifier=u'abide_category_pdd_nos_asperger',
                                          name=u'Diagnostic category Aspergers or PDD-NOS').eid
    categories['u'] = store.create_entity('Group', identifier=u'abide_category_unknown',
                                          name=u'Diagnostic category unknown').eid
    return groups, categories

def create_score_defs(store):
    score_defs = {}
    # Various scores
    score_defs['dx_group'] = store.create_entity('ScoreDefinition', name=u'Diagnostic Group',
                                                  category=u'biological', type=u'numerical',
                                                  possible_values=u'1 = Autism; 2 = Control').eid
    score_defs['dsm_iv_tr'] = store.create_entity('ScoreDefinition', name=u'DSM-IV-TR Diagnostic Category',
                                                  category=u'biological', type=u'numerical',
                                                  possible_values=u'0 = Control; 1 = Autism; 2 = Aspergers; 3 = PDD-NOS; 4 = Aspergers or PDD-NOS').eid
    score_defs['handedness_score'] = store.create_entity('ScoreDefinition', name=u'Subject Handedness Score',
                                                         category=u'biological', type=u'numerical',
                                                         possible_values=u'Positive number = Right;\
                                                         Negative number = Left; 0 = Ambidextrous').eid
    score_defs['scq_total'] = store.create_entity('ScoreDefinition', name=u'Social Communication Questionnaire Total',
                                                  category=u'behavioral', type=u'numerical',
                                                  possible_values=u'0-39').eid
    score_defs['aq_total'] = store.create_entity('ScoreDefinition', name=u'Total Raw Score of the Autism Quotient',
                                                  category=u'behavioral', type=u'numerical',
                                                  possible_values=u'0-50').eid
    score_defs['comorbidity'] = store.create_entity('ScoreDefinition', name=u'Any other comorbidities ?',
                                                    category=u'biological', type=u'string').eid
    score_defs['current_med_status'] = store.create_entity('ScoreDefinition', name=u'Currently Taking Medications ?',
                                                           category=u'biological', type=u'numerical',
                                                           possible_values=u'0 = not taking medication; 1 = taking medication').eid
    score_defs['medication_name'] = store.create_entity('ScoreDefinition', name=u'Active ingredient of any current psychoactive medications',
                                                        category=u'biological', type=u'string').eid
    score_defs['off_stimulants_at_scan'] = store.create_entity('ScoreDefinition', name=u'Off stimulants 24 hours prior to scan ?',
                                                               category=u'biological', type=u'numerical',
                                                               possible_values=u'0 = no; 1 = yes').eid
    score_defs['eye_status_at_scan'] = store.create_entity('ScoreDefinition', name=u'Eye Status During Rest Scan',
                                                               category=u'behavioral', type=u'numerical',
                                                               possible_values=u'1 = open; 2 = closed').eid
    score_defs['age_at_mprage'] = store.create_entity('ScoreDefinition', name=u'Age at Anatomical Scan in years',
                                                               category=u'biological', type=u'numerical').eid
    score_defs['bmi'] = store.create_entity('ScoreDefinition', name=u'Body Mass Index',
                                            category=u'biological', type=u'numerical').eid

    # FIQ/VIQ/PIQ scores
    for test_type in (u'DAS_II_SA', u'GIT', u'HAWIK', u'WAIS_III', u'WASI',
                      # XXX WAIS/WISC are not defined in the specs...
                      u'WAIS', u'WISC', u'WISC_IV_FULL', u'HAWIK_IV',
                      u'WISC_III', u'WISC_III_DUTCH', u'WISC_IV_4_SUBTESTS',
                      u'WISCC_IV_FULL', u'WST'):
        name = u'FIQ Standard Score - %s' % test_type
        score_defs['fiq_%s' % test_type.lower()] = store.create_entity('ScoreDefinition', name=name,
                                                                       category=u'FIQ',
                                                                       type=u'numerical').eid
    for test_type in (u'DAS_II_SA', u'GIT', u'HAWIK', u'PPVT', u'WAIS_III', u'WASI',
                      # XXX WAIS/WISC are not defined in the specs...
                      u'WAIS', u'WISC', u'WISC_IV_FULL',
                      u'WISC_III', u'WISC_III_DUTCH', u'WISC_IV_4_SUBTESTS',
                      u'WISCC_IV_FULL', u'WST'):
        name = u'VIQ Standard Score - %s' % test_type
        score_defs['viq_%s' % test_type.lower()] = store.create_entity('ScoreDefinition', name=name,
                                                                       category=u'VIQ',
                                                                       type=u'numerical').eid
    for test_type in (u'DAS_II_SA', u'GIT', u'HAWIK', u'RAVENS', u'WAIS_III', u'WASI',
                      # XXX WAIS/WISC are not defined in the specs...
                      u'WAIS', u'WISC', u'WISC_IV_FULL',
                      u'WISC_III', u'WISC_III_DUTCH', u'WISC_IV_4_SUBTESTS',
                      u'WISCC_IV_FULL', u'WST'):
        name = u'PIQ Standard Score - %s' % test_type
        score_defs['piq_%s' % test_type.lower()] = store.create_entity('ScoreDefinition', name=name,
                                                                       category=u'PIQ',
                                                                       type=u'numerical').eid
    return score_defs


###############################################################################
### QUESTIONNAIRES ############################################################
###############################################################################
def create_adi_questionnaire(store):
    """Create a questionnaire for adi"""
    questionnaire_eid = store.create_entity('Questionnaire',
                                            name=u'Autism Diagnostic Interview-Revised (ADI)',
                                            identifier=u'abide_adi', type=u'behavioral').eid
    questions = {}
    text = u'Reciprocal Social Interaction Subscore (A) Total for Autism Diagnostic Interview-Revised'
    questions['adi_r_social_total_a'] = store.create_entity('Question',
                                                            identifier=u'adi_r_social_total_a',
                                                            position=0, text=text,
                                                            type=u'numerical',
                                                            questionnaire=questionnaire_eid,
                                                            possible_answers=u'0-30').eid
    text = u'Abnormalitites in Communication Subscore (B) Total for Autism Diagnostic Interview-Revised',
    questions['adi_r_verbal_total_bv'] = store.create_entity('Question',
                                                            identifier=u'adi_r_verbal_total_bv',
                                                            position=1, text=text,
                                                            type=u'numerical',
                                                            questionnaire=questionnaire_eid,
                                                            possible_answers=u'0-26').eid
    text = u'Restricted, Repetitive and Stereotyped Patters of Behavior Subscore (C) Total for Autism Diagnostic Interview-Revised'
    questions['adi_r_rrb_total_c'] = store.create_entity('Question',
                                                         identifier=u'adi_r_rrb_total_c',
                                                         position=2, text=text,
                                                         type=u'numerical',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'0-12').eid
    text = u'Abnormality of Development Evident at or Before 36 Monts Subscore (D) Total for Autism Diagnostic Interview-Revised'
    questions['adi_r_onset_total_d'] = store.create_entity('Question',
                                                         identifier=u'adi_r_onset_total_d',
                                                         position=3, text=text,
                                                         type=u'numerical',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'0-5').eid
    text = u'Was ADI scored and administered by research reliable personnel?'
    questions['adi_r_rsrch_reliable'] = store.create_entity('Question',
                                                         identifier=u'adi_r_rsrch_reliable',
                                                         position=4, text=text,
                                                         type=u'boolean',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'0 = not research reliable; 1 = research reliable').eid
    return questionnaire_eid, questions

def create_ados_questionnaire(store):
    """Create a questionnaire for ados"""
    questionnaire_eid = store.create_entity('Questionnaire',
                                            name=u'Autism Diagnostic Observation Schedule Module (ADOS)',
                                            identifier=u'abide_ados', type=u'behavioral').eid
    questions = {}
    text = u'Autism Diagnostic Observation Schedule Module'
    questions['ados_module'] = store.create_entity('Question',
                                                   identifier=u'ados_module',
                                                   position=0, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-4').eid
    text = u'Classical Total ADOS Score (Communication subscore + Social Interaction subscore)'
    questions['ados_total'] = store.create_entity('Question',
                                                   identifier=u'ados_total',
                                                   position=1, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'0-22').eid
    text = u'Communication Total Subscore of the Classic ADOS'
    questions['ados_comm'] = store.create_entity('Question',
                                                 identifier=u'ados_comm',
                                                 position=2, text=text,
                                                 type=u'numerical',
                                                 questionnaire=questionnaire_eid,
                                                 possible_answers=u'0-8').eid
    text = u'Social Total Subscore of the Classic ADOS'
    questions['ados_social'] = store.create_entity('Question',
                                                 identifier=u'ados_social',
                                                 position=3, text=text,
                                                 type=u'numerical',
                                                 questionnaire=questionnaire_eid,
                                                 possible_answers=u'0-14').eid
    text = u'Stereotyped Behaviors and Restricted Interests Total Subscore of the Classic ADOS'
    questions['ados_stereo_behav'] = store.create_entity('Question',
                                                 identifier=u'ados_stereo_behav',
                                                 position=4, text=text,
                                                 type=u'numerical',
                                                 questionnaire=questionnaire_eid,
                                                 possible_answers=u'0-8').eid
    text = u'Was ADOS scored and administered by research reliable personnel?'
    questions['ados_rsrch_reliable'] = store.create_entity('Question',
                                                           identifier=u'ados_rsrch_reliable',
                                                           position=5, text=text,
                                                           type=u'boolean',
                                                           questionnaire=questionnaire_eid,
                                                           possible_answers=u'0 = not research reliable; 1 = research reliable').eid
    text = u'Social Affect Total Subscore for Gotham Algorithm of the ADOS'
    questions['ados_gotham_soc_affect'] = store.create_entity('Question',
                                                              identifier=u'ados_gotham_soc_affect',
                                                              position=6, text=text,
                                                              type=u'numerical',
                                                              questionnaire=questionnaire_eid,
                                                              possible_answers=u'0-20').eid
    text = u'Restrictive and Repetitive Behaviors Total Subscore for Gotham Algorithm of the ADOS'
    questions['ados_gotham_rrb'] = store.create_entity('Question',
                                                         identifier=u'ados_gotham_rrb',
                                                         position=7, text=text,
                                                         type=u'numerical',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'0-8').eid
    text = u'Social Affect Total + Restricted and Repetitive Behaviors Total'
    questions['ados_gotham_total'] = store.create_entity('Question',
                                                         identifier=u'ados_gotham_total',
                                                         position=8, text=text,
                                                         type=u'numerical',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'0-28').eid
    text = u'Individually Calibrated Severity Score for Gotham Algorithm of the ADOS'
    questions['ados_gotham_severity'] = store.create_entity('Question',
                                                         identifier=u'ados_gotham_severity',
                                                         position=9, text=text,
                                                         type=u'numerical',
                                                         questionnaire=questionnaire_eid,
                                                         possible_answers=u'1-10').eid
    return questionnaire_eid, questions

def create_srs_questionnaire(store):
    """Create a questionnaire for srs"""
    questionnaire_eid = store.create_entity('Questionnaire',
                                            name=u'Social Responsiveness Scale Version',
                                            identifier=u'avide_srs', type=u'behavioral').eid
    questions = {}
    text = u'Social Responsiveness Scale Version'
    questions['srs_version'] = store.create_entity('Question',
                                                   identifier=u'srs_version',
                                                   position=0, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1 = child; 2 = adult').eid
    text = u'Total Raw Score the Social Responsiveness Scale'
    questions['srs_raw_total'] = store.create_entity('Question',
                                                   identifier=u'srs_raw_total',
                                                   position=1, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'0 >= 117').eid
    text = u'Social Responsiveness Scale Social Avareness Subscore Raw Total'
    questions['srs_awareness'] = store.create_entity('Question',
                                                   identifier=u'srs_awareness',
                                                   position=2, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'0 >= 19').eid
    text = u'Social Responsiveness Scale Social Cognition Subscore Raw Total'
    questions['srs_cognition'] = store.create_entity('Question',
                                                     identifier=u'srs_cognition',
                                                     position=3, text=text,
                                                     type=u'numerical',
                                                     questionnaire=questionnaire_eid,
                                                     possible_answers=u'0 >= 24').eid
    text = u'Social Responsiveness Scale Social Communication Subscore Raw Total'
    questions['srs_communication'] = store.create_entity('Question',
                                                     identifier=u'srs_communication',
                                                     position=4, text=text,
                                                     type=u'numerical',
                                                     questionnaire=questionnaire_eid,
                                                     possible_answers=u'0 >= 43').eid
    text = u'Social Responsiveness Scale Social Motivation Subscore Raw Total'
    questions['srs_motivation'] = store.create_entity('Question',
                                                     identifier=u'srs_motivation',
                                                     position=5, text=text,
                                                     type=u'numerical',
                                                     questionnaire=questionnaire_eid,
                                                     possible_answers=u'0 >= 22').eid
    text = u'Social Responsiveness Scale Social Autistic Mannerisms Subscore Raw Total'
    questions['srs_mannerisms'] = store.create_entity('Question',
                                                     identifier=u'srs_mannerisms',
                                                     position=6, text=text,
                                                     type=u'numerical',
                                                     questionnaire=questionnaire_eid,
                                                     possible_answers=u'0 >= 22').eid
    return questionnaire_eid, questions

def create_vineland_questionnaire(store):
    """Create a questionnaire for vineland"""
    questionnaire_eid = store.create_entity('Questionnaire',
                                            name=u'Vineland Adaptive Behavior Scales',
                                            identifier=u'avide_vineland', type=u'behavioral').eid
    questions = {}
    text = u'Vineland Adaptive Behavior Scales Receptive Language V Scaled Score'
    questions['vineland_receptive_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_receptive_v_scaled',
                                                                   position=0, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Expressive Language V Scaled Score'
    questions['vineland_expressive_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_expressive_v_scaled',
                                                                   position=1, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Written Language V Scaled Score'
    questions['vineland_written_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_written_v_scaled',
                                                                   position=2, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Communication Standard Score'
    questions['vineland_communication_standard'] = store.create_entity('Question',
                                                                   identifier=u'vineland_communication_standard',
                                                                   position=3, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'20-160').eid
    text = u'Vineland Adaptive Behavior Scales Personal Daily Living Skills V Scaled Score'
    questions['vineland_personal_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_personal_v_scaled',
                                                                   position=4, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Domestic Daily Living Skills V Scaled Score'
    questions['vineland_domestic_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_domestic_v_scaled',
                                                                   position=5, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Community Daily Living Skills V Scaled Score'
    questions['vineland_community_v_scaled'] = store.create_entity('Question',
                                                                   identifier=u'vineland_community_v_scaled',
                                                                   position=6, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Daily Living Skills Standard Score'
    questions['vineland_dailylvng_standard'] = store.create_entity('Question',
                                                                   identifier=u'vineland_dailylvng_standard',
                                                                   position=7, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'20-160').eid
    text = u'Vineland Adaptive Behavior Scales Interpersonal Relationships V Scaled Score'
    questions['vineland_interpersonal_v_scaled'] = store.create_entity('Question',
                                                                       identifier=u'vineland_interpersonal_v_scaled',
                                                                       position=8, text=text,
                                                                       type=u'numerical',
                                                                       questionnaire=questionnaire_eid,
                                                                       possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Play and Leisure Time V Scaled Score'
    questions['vineland_play_v_scaled'] = store.create_entity('Question',
                                                             identifier=u'vineland_play_v_scaled',
                                                             position=9, text=text,
                                                             type=u'numerical',
                                                             questionnaire=questionnaire_eid,
                                                             possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior ScalesCoping Skills V Scaled Score'
    questions['vineland_coping_v_scaled'] = store.create_entity('Question',
                                                             identifier=u'vineland_coping_v_scaled',
                                                             position=10, text=text,
                                                             type=u'numerical',
                                                             questionnaire=questionnaire_eid,
                                                             possible_answers=u'1-24').eid
    text = u'Vineland Adaptive Behavior Scales Socialization Standard Score'
    questions['vineland_social_standard'] = store.create_entity('Question',
                                                                   identifier=u'vineland_social_standard',
                                                                   position=11, text=text,
                                                                   type=u'numerical',
                                                                   questionnaire=questionnaire_eid,
                                                                   possible_answers=u'20-160').eid
    text = u'Sum of Vineland Standard Scores (Communication + Daily Living Skills + Socialization)'
    questions['vineland_sum_scores'] = store.create_entity('Question',
                                                           identifier=u'vineland_sum_scores',
                                                           position=12, text=text,
                                                           type=u'numerical',
                                                           questionnaire=questionnaire_eid,
                                                           possible_answers=u'76-480').eid
    text = u'Vineland Adaptive Behavior Composite Standard score'
    questions['vineland_abc_standard'] = store.create_entity('Question',
                                                           identifier=u'vineland_abc_standard',
                                                           position=13, text=text,
                                                           type=u'numerical',
                                                           questionnaire=questionnaire_eid,
                                                           possible_answers=u'20-160').eid
    text = u'Vineland Adaptive Behavior Scales Informant'
    questions['vineland_informant'] = store.create_entity('Question',
                                                           identifier=u'vineland_informant',
                                                           position=14, text=text,
                                                           type=u'numerical',
                                                           questionnaire=questionnaire_eid,
                                                           possible_answers=u'1 = parent; 2 = self').eid
    return questionnaire_eid, questions

def create_wisc_iv_questionnaire(store):
    """Create a questionnaire for wisc_iv"""
    questionnaire_eid = store.create_entity('Questionnaire', name=u'WISC-IV',
                                            identifier=u'avide_wisc_iv', type=u'behavioral').eid
    questions = {}
    text = u'WISC-IV Verbal Comprehension Index'
    questions['wisc_iv_vci'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_vci',
                                                   position=0, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'3-57').eid
    text = u'WISC-IV Perceptual Reasoning Index'
    questions['wisc_iv_pri'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_pri',
                                                   position=1, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'3-57').eid
    text = u'WISC-IV Working Memory Index'
    questions['wisc_iv_wmi'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_wmi',
                                                   position=2, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'2-38').eid
    text = u'WISC-IV Processing Speed Index'
    questions['wisc_iv_psi'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_psi',
                                                   position=3, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'2-38').eid
    text = u'WISC-IV Sim Scaled'
    questions['wisc_iv_sim_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_sim_scaled',
                                                   position=4, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Vocabulary Scaled'
    questions['wisc_iv_vocab_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_vocab_scaled',
                                                   position=5, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Information Scaled'
    questions['wisc_iv_info_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_info_scaled',
                                                   position=6, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Block Design Scaled'
    questions['wisc_iv_blk_dsn_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_blk_dsn_scaled',
                                                   position=7, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Picture Concepts Scaled'
    questions['wisc_iv_pic_con_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_pic_con_scaled',
                                                   position=8, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Matrix Reasoning Scaled'
    questions['wisc_iv_matrix_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_matrix_scaled',
                                                   position=9, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Digit Span Scaled'
    questions['wisc_iv_digit_span_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_digit_span_scaled',
                                                   position=10, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Letter-Number Sequencing Scaled'
    questions['wisc_iv_let_num_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_let_num_scaled',
                                                   position=11, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Coding Scaled'
    questions['wisc_iv_coding_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_coding_scaled',
                                                   position=12, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    text = u'WISC-IV Symbol Search Scaled'
    questions['wisc_iv_sym_scaled'] = store.create_entity('Question',
                                                   identifier=u'wisc_iv_sym_scaled',
                                                   position=13, text=text,
                                                   type=u'numerical',
                                                   questionnaire=questionnaire_eid,
                                                   possible_answers=u'1-19').eid
    return questionnaire_eid, questions


def import_questionnaire(store, subject_eid, center_eid, studies_eids, questionnaire_eid,
                         questions, answers_listing, subj_id, label, valid_ind, user_ident=None):
    assessment = store.create_entity('Assessment', identifier=u'%s_%s' % (label, subj_id),
                                     # XXX datetime, timepoint
                                     protocol=u'ABIDE')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    if valid_ind:
        valid = bool(int(line[valid_ind])) if line[valid_ind] else False
    else:
        valid = True
    if user_ident:
        user_ident = u'parent' if line[user_ident] == '1' else u'subject'
    else:
        user_ident = u'subject'
    adi_qrun = store.create_entity('QuestionnaireRun', identifier=u'%s_%s' % (label, subj_id),
                                   user_ident=user_ident,
                                   # XXX datetime
                                   iteration=1, completed=True, valid=valid,
                                   instance_of=questionnaire_eid)
    for eid in studies_eids:
        store.relate(adi_qrun.eid, 'related_study', eid)
    store.relate(adi_qrun.eid, 'concerns', subject_eid, subjtype='QuestionnaireRun')
    store.relate(assessment.eid, 'generates', adi_qrun.eid, subjtype='Assessment')
    for ind, name in answers_listing:
        # Always create answer, even if without value
        score_value = store.create_entity('Answer', value=float(line[ind]) if line[ind] else None,
                                          # XXX datetime
                                          question=questions[name],
                                          questionnaire_run=adi_qrun.eid)


###############################################################################
### IMAGES ####################################################################
###############################################################################
def import_images(store, pdf_eid, subject_eid, center_eid, study_eid, abide_study, images_dict, subj_id, label):
    assessment = store.create_entity('Assessment', identifier=u'%s_%s' % (label, subj_id),
                                     # XXX datetime, timepoint
                                     protocol=u'ABIDE')
    store.relate(center_eid, 'holds', assessment.eid)
    store.relate(subject_eid, 'concerned_by', assessment.eid)
    store.relate(assessment.eid, 'external_resources', pdf_eid)
    image_path = images_dict.get(subj_id)
    if image_path:
        scan_data, mri_data = {}, {}
        if label == 'anatomy':
            mri_data['sequence'] = u'T1'
            scan_data['label'] = u'anatomy'
            scan_data['type'] = u'normalized T1'
        else: # Rest
            mri_data['sequence'] = u'resting-state'
            scan_data['label'] = u'resting-state'
            scan_data['type'] = u'resting-state'
        mri_data.update(get_image_info(image_path))
        scan_data['filepath'] = osp.relpath(image_path)
        # Data properties
        scan_data['identifier'] = u'%s_%s' % (label, subj_id)
        scan_data['format'] = u'nii.gz'
        scan_data['completed'] = True
        scan_data['valid'] = True
        # Create entity
        mri_data = store.create_entity('MRIData', **mri_data)
        scan_data['has_data'] = mri_data.eid
        scan_data['related_study'] = study_eid
        scan_data = store.create_entity('Scan', **scan_data)
        store.relate(scan_data.eid, 'concerns', subject_eid, subjtype='Scan')
        store.relate(scan_data.eid, 'other_studies', abide_study, subjtype='Scan')
        # XXX device
        #store.relate(scan_data.eid, 'uses_device', device_id)
        store.relate(assessment.eid, 'generates', scan_data.eid, subjtype='Assessment')




###############################################################################
### STUDIES/CENTERS/INVESTIGATORS #############################################
###############################################################################
def create_abide_study(store):
    # Create the Abide study
    abide_study_eid = store.create_entity('Study', name=u'Abide',
                                          data_filepath=unicode(base_path),
                                          keywords=u'Abide; ASD',
                                          description=u'''The complexity and heterogeneity of ASD make it necessary to obtain large-scale samples which are difficult to attain in any individual lab. In response, the Autism Brain Imaging Data Exchange (ABIDE) hereby provides previously collected resting state functional magnetic resonance imaging (R-fMRI) datasets from 539 individuals with ASD and 573 typical controls for the purpose of data sharing in the broader scientific community. This grass-root initiative involved 16 international sites, sharing 20 samples yielding 1112 datasets composed of both MRI data and an extensive array of phenotypic information common across nearly all sites (see below). This unprecedented effort is expected to facilitate discovery science and comparisons across samples. In accordance with HIPAA guidelines and 1000 Functional Connectomes Project / INDI protocols, all datasets are anonymous, with no protected health information included. See fcon_1000.projects.nitrc.org/indi/abide''').eid
    theme_eid = store.create_entity('Theme', name=u'Autism spectrum disorders (ASD)',
                                    description=u'''Autism spectrum disorders (ASD) are characterized by qualitative impairment in reciprocal social communication, as well as by repetitive, restricted, and stereotyped behaviors. Previously considered rare, ASD are now recognized to occur in more than 1% of children, causing immense suffering to individuals and their families.''').eid
    store.relate(abide_study_eid, 'themes', theme_eid)
    return abide_study_eid

# XXX Centers/Investigators ?

def create_devices(store):
    devices = {}
    devices['anat_CMU'] = store.create_entity('Device', name=u'SIEMENS MAGNETOM Verio syngo MR B17',
                                              manufacturer=u'SIEMENS', model=u'MAGNETOM Verio').eid
    # configurations/hosted_by

###############################################################################
### MAIN ######################################################################
###############################################################################
if __name__ == '__main__':
    base_path = osp.abspath(sys.argv[4])
    store = Store(session)
    count_all_subject = 0
    # Create groups and categories
    groups, categories = create_groups_and_categories(session)
    # Create score defs
    score_defs = create_score_defs(session)
    # Questionnaire
    adi_questionnaire, adi_questions = create_adi_questionnaire(store)
    ados_questionnaire, ados_questions = create_ados_questionnaire(store)
    srs_questionnaire, srs_questions = create_srs_questionnaire(store)
    vineland_questionnaire, vineland_questions = create_vineland_questionnaire(store)
    wisc_iv_questionnaire, wisc_iv_questions = create_wisc_iv_questionnaire(store)
    # Create the Abide study
    abide_study_eid = create_abide_study(store)
    # Studies
    studies = {}
    # Centers
    centers = {}
    # Get all image files
    mprages = {}
    for img_path in glob.iglob(os.path.join(base_path, '*/*/session_1/anat_1/mprage.nii.gz')):
        subj_id =  str(int(img_path.split('/session_1/anat_1')[0].split('/')[-1]))
        mprages[subj_id] = img_path
    rests = {}
    for img_path in glob.iglob(os.path.join(base_path, '*/*/session_1/rest_1/rest.nii.gz')):
        subj_id =  str(int(img_path.split('/session_1/rest_1')[0].split('/')[-1]))
        rests[subj_id] = img_path
    # Import all subjects
    study_csv_file = osp.join(base_path, 'Phenotypic_V1_0b.csv')
    fobj = open(study_csv_file, 'rU')
    csvr = csv.reader(fobj, delimiter=',', dialect=csv.excel_tab)
    # Create subjects
    subjects = {}
    anat_pdf = {}
    rest_pdf = {}
    # IMPORT ##################################################################
    for ind_line, line in enumerate(csvr):
        if ind_line == 0:
            # Skip first line
            continue
        # SUBJECTS ############################################################
        print line[:15]
        subj_id = unicode(line[1])
        subject_eid = store.create_entity('Subject', identifier=subj_id,
                                          age=int(round(float(line[4]))),
                                          gender=SEX.get(line[5]),
                                          handedness=HANDEDNESS.get(line[6], u'unknown')).eid
        subjects[subj_id] = subject_eid
        # Related studies
        store.relate(subject_eid, 'related_studies', abide_study_eid)
        if line[0] in studies:
            store.relate(subject_eid, 'related_studies', studies[line[0]])
            anat_pdf_eid = anat_pdf.get(line[0])
            rest_pdf_eid = anat_pdf.get(line[0])
        else:
            study_eid = store.create_entity('Study', name=u'Abide - %s' % line[0],
                                            data_filepath=unicode(base_path)).eid
            studies[line[0]] = study_eid
            store.relate(subject_eid, 'related_studies', study_eid)
            # Create/Get files
            anat_pdf_eid = store.create_entity('ExternalResource', name=u'Abide - %s - Anat pdf' % line[0],
                                               related_study=study_eid,
                                               filepath=osp.relpath(u'%s_anat.pdf' % line[0])).eid
            anat_pdf[line[0]] = anat_pdf_eid
            rest_pdf_eid = store.create_entity('ExternalResource', name=u'Abide - %s - Rest pdf' % line[0],
                                               related_study=study_eid,
                                               filepath=osp.relpath(u'%s_rest.pdf' % line[0])).eid
            rest_pdf[line[0]] = rest_pdf_eid
        # Center
        if line[0] in centers:
            center_eid = centers[line[0]]
        else:
            center_eid = store.create_entity('Center', identifier=unicode(line[0]),
                                            name=unicode(line[0])).eid
            centers[line[0]] = center_eid
        # GROUPS/CATEGORIES ###################################################
        store.relate(subject_eid, 'related_groups', groups[int(line[2])])
        if line[3] in categories:
            store.relate(subject_eid, 'related_groups', categories[line[3]])
        else:
            store.relate(subject_eid, 'related_groups', categories['u'])
        # Numerical scores
        for ind, label in ((2, 'dx_group'),
                           (3, 'dsm_iv_tr'),
                           (7, 'handedness_score'),
                           (36, 'scq_total'),
                           (37, 'aq_total'),
                           (39, 'current_med_status'),
                           (41, 'off_stimulants_at_scan'),
                           (71, 'eye_status_at_scan'),
                           (72, 'age_at_mprage'),
                           (73, 'bmi'),
                           ):
            if line[ind]:
                try:
                    v = float(line[ind])
                    score_value = store.create_entity('ScoreValue',
                                                      definition=score_defs[label],
                                                      value=v).eid
                    store.relate(subject_eid, 'related_infos', score_value)
                except:
                    continue
        # String scores
        # XXX Use questionnaire for medication name ?
        for ind, label in ((38, 'comorbidity'),
                           (40, 'medication_name'),):
            if line[ind]:
                score_value = store.create_entity('ScoreValue',
                                                  definition=score_defs[label],
                                                  text=line[ind]).eid
                store.relate(subject_eid, 'related_infos', score_value)
        # FIQ/VIQ/PIQ SCORES ##################################################
        for vind, tind, label in ((8, 11, 'fiq'), (9, 12, 'viq'), (10, 13, 'piq')):
            if line[tind] and line[vind]:
                definition = score_defs.get('%s_%s' % (label, line[tind].lower()))
                if definition:
                    score_value = store.create_entity('ScoreValue',
                                                      definition=definition,
                                                      value=line[vind]).eid
                    store.relate(subject_eid, 'related_infos', score_value)
                else:
                    print 'Unknown ', label, line[vind], line[tind]
        # ADI SCORES ##########################################################
        adi_answers_listing = ((14, 'adi_r_social_total_a'),
                               (15, 'adi_r_verbal_total_bv'),
                               (16, 'adi_r_rrb_total_c'),
                               (17, 'adi_r_onset_total_d'),
                               (18, 'adi_r_rsrch_reliable'))
        import_questionnaire(store, subject_eid, center_eid, (study_eid, abide_study_eid),
                             adi_questionnaire,
                             adi_questions, adi_answers_listing, subj_id, 'adi', 18)
        # ADOS SCORES ##########################################################
        ados_answers_listing = ((19, 'ados_module'),
                                (20, 'ados_total'),
                                (21, 'ados_comm'),
                                (22, 'ados_social'),
                                (23, 'ados_stereo_behav'),
                                (24, 'ados_rsrch_reliable'),
                                (25, 'ados_gotham_soc_affect'),
                                (26, 'ados_gotham_rrb'),
                                (27, 'ados_gotham_total'),
                                (28, 'ados_gotham_severity'),)
        import_questionnaire(store, subject_eid, center_eid, (study_eid, abide_study_eid),
                             ados_questionnaire,
                             ados_questions, ados_answers_listing, subj_id, 'ados', 24)
        # SRS SCORES ##########################################################
        srs_answers_listing = ((29, 'srs_version'),
                               (30, 'srs_raw_total'),
                               (31, 'srs_awareness'),
                               (32, 'srs_cognition'),
                               (33, 'srs_communication'),
                               (34, 'srs_motivation'),
                               (35, 'srs_mannerisms'),)
        import_questionnaire(store, subject_eid, center_eid, (study_eid, abide_study_eid),
                             srs_questionnaire,
                             srs_questions, srs_answers_listing, subj_id, 'srs', None)
        # VINELAND SCORES ##########################################################
        vineland_answers_listing = ((42, 'vineland_receptive_v_scaled'),
                                    (43, 'vineland_expressive_v_scaled'),
                                    (44, 'vineland_written_v_scaled'),
                                    (45, 'vineland_communication_standard'),
                                    (46, 'vineland_personal_v_scaled'),
                                    (47, 'vineland_domestic_v_scaled'),
                                    (48, 'vineland_community_v_scaled'),
                                    (49, 'vineland_dailylvng_standard'),
                                    (50, 'vineland_interpersonal_v_scaled'),
                                    (51, 'vineland_play_v_scaled'),
                                    (52, 'vineland_coping_v_scaled'),
                                    (53, 'vineland_social_standard'),
                                    (54, 'vineland_sum_scores'),
                                    (55, 'vineland_abc_standard'),
                                    (56, 'vineland_informant'),)
        import_questionnaire(store, subject_eid, center_eid, (study_eid, abide_study_eid),
                             vineland_questionnaire,
                             vineland_questions, vineland_answers_listing, subj_id, 'vineland', None, 56)
        # WISC_IV SCORES ##########################################################
        wisc_iv_answers_listing = ((57, 'wisc_iv_vci'),
                                   (58, 'wisc_iv_pri'),
                                   (59, 'wisc_iv_wmi'),
                                   (60, 'wisc_iv_psi'),
                                   (61, 'wisc_iv_sim_scaled'),
                                   (62, 'wisc_iv_vocab_scaled'),
                                   (63, 'wisc_iv_info_scaled'),
                                   (64, 'wisc_iv_blk_dsn_scaled'),
                                   (65, 'wisc_iv_pic_con_scaled'),
                                   (66, 'wisc_iv_matrix_scaled'),
                                   (67, 'wisc_iv_digit_span_scaled'),
                                   (68, 'wisc_iv_let_num_scaled'),
                                   (69, 'wisc_iv_coding_scaled'),
                                   (70, 'wisc_iv_sym_scaled'),)
        import_questionnaire(store, subject_eid, center_eid, (study_eid, abide_study_eid),
                             wisc_iv_questionnaire,
                             wisc_iv_questions, wisc_iv_answers_listing, subj_id, 'wisc_iv', None, None)
        # IMAGES ##############################################################
        import_images(store, anat_pdf_eid, subject_eid, center_eid, study_eid,
                      abide_study_eid, mprages, subj_id, 'anatomy')
        import_images(store, rest_pdf_eid, subject_eid, center_eid, study_eid,
                      abide_study_eid, rests, subj_id, 'resting-state')


    # Flush and commit
    store.flush()
    store.commit()
