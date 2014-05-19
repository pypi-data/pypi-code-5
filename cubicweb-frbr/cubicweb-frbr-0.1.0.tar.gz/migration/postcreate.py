# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-frbr postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""
import os.path as osp
import codecs

from cubicweb import dataimport as cwdi


def _import_langs(session, lang_file):
    """ Import a language file """
    with codecs.open(lang_file, encoding='utf-8') as lines:
        for line in lines:
            row = line.strip().split('|')
            if len(row[0]) > 3:
                row[0] = row[0].split('-')[0]
            code1, code2, code3, en_label, fr_label = row
            session.create_entity('Language', code=code1, code2=code2, code3=code3, name=fr_label,
                                  cwuri=u'http://id.loc.gov/vocabulary/iso639-2/%s' % code1)

def _import_countries(session, country_file):
    """ Import a country file """
    for row in cwdi.ucsvreader(open(country_file), encoding='utf-8'):
        if len(row) == 2:
            code, label = row
            altlabels = u''
        else:
            code, label, altlabels = row
        session.create_entity('Country', code=code, name=label, altlabels=altlabels,
                              cwuri='http://id.loc.gov/vocabulary/countries/%s' % code)

def _import_dewey(session, dewey_file):
    """ Import a dewey file """
    for row in cwdi.ucsvreader(open(dewey_file), encoding='utf-8'):
        code, label = row[0].strip(), row[1].strip()
        session.create_entity('Dewey', code=code, name=label,
                              cwuri=u'http://dewey.info/class/%s/' % code)

def _import_scripts(session, script_file):
    """ Import a script file - From Musicbrainz """
    for row in cwdi.ucsvreader(open(script_file), separator='\t', encoding='utf-8'):
        try:
            frequency = int(row[4])
        except ValueError:
            frequency = None
        session.create_entity('Script', code=row[1], iso_number=int(row[2]),
                              name=row[3], frequency=frequency)

def _import_role(session, role_file, idloc_file):
    """ Import a role file"""
    code_idloc = dict([code, idloc] for code, idloc in cwdi.ucsvreader(open(idloc_file), separator=','))
    for row in cwdi.ucsvreader(open(role_file), encoding='utf-8'):
        code, label = row
        sort_key = 10000*int(code[-1]) + int(code)
        if code == '0070':
            sort_key = 100001
        if code == '9990':
            sort_key = 100002
            label = u'Autre'
        try:
            cwuri = u'http://data.bnf.fr/vocabulary/roles/r%s' % int(code)
        except:
            continue
        session.create_entity('Role', cwuri=cwuri, code=code, name=label,
                              sort_key=sort_key, idloc=code_idloc.get(code))

HERE = osp.join(osp.abspath(osp.dirname(__file__)))
_import_langs(session, osp.join(HERE, 'ISO-639-2_utf-8.txt'))
_import_countries(session, osp.join(HERE, 'ISO-3166-alpha2_utf-8.txt'))
_import_dewey(session, osp.join(HERE, 'ref_domaines.csv'))
_import_scripts(session, osp.join(HERE, 'scripts.txt'))
_import_role(session, osp.join(HERE, 'ref_roles.csv'), osp.join(HERE, 'codes_marc_idlocgov.csv'))
