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
from cubicweb.selectors import is_instance
from cubicweb.web.views.tableview import EntityTableView, RelationColRenderer


###############################################################################
### GENOMIC MEASURE - CGH #####################################################
###############################################################################
class AbstractCghTableView(EntityTableView):
    __abtract__ = True
    __select__ = EntityTableView.__select__ & is_instance('CghResult')


class CghTableView(AbstractCghTableView):
    __regid__ = 'cgh-table-view'
    columns = ['related_gene', 'cgh_ratio']
    column_renderers = {'related_gene': RelationColRenderer(role='subject')}


class GeneCghTableView(AbstractCghTableView):
    __regid__ = 'gene-cgh-table-view'
    columns = ['related_measure', 'cgh_ratio']
    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext')}


###############################################################################
### GENOMIC MEASURE - SEQUENCAGE ##############################################
###############################################################################
class AbstractMutationTableView(EntityTableView):
    __abstract__ = True
    __select__ = EntityTableView.__select__ & is_instance('Mutation')

    columns = ['histology_number', 'biopsy_date', 'percent_tumoral',
               'valid', 'mutation_id', 'mutation_type', 'ploidy',
               'reference_base', 'variant_base', 'variant_frequency', 'p_value',
               'coverage', 'reference_coverage', 'variant_coverage',
               'hotspot_id', 'reference_id', 'comment',
               'protein', 'biological_classification', 'classification_type',
               'locus_version', 'nucl', 'polyphen', 'sift', 'gvd_alignment',
               'base', 'conclusions', 'reception_date', 'result_date',
               'block', 'medical_coverage', 'transfert']


class MutationTableView(AbstractMutationTableView):
    __regid__ = 'mutation-table-view'

    column_renderers = {'related_gene': RelationColRenderer(role='subject')}

    columns = ['related_gene',] + AbstractMutationTableView.columns


class GeneMutationTableView(AbstractMutationTableView):
    __regid__ = 'gene-mutation-table-view'

    column_renderers = {'related_measure': RelationColRenderer(role='subject', vid='incontext')}

    columns = ['related_measure',] + AbstractMutationTableView.columns
