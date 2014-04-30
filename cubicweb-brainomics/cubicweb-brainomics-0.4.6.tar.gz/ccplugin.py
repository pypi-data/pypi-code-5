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


import os
from os import path as osp
import shutil
import logging
import csv
from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.utils import make_uid
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL, check_options_consistency


def copy_file(old_fpath, new_fpath, logger=None):
    """Safe copy of a file from one path to another
    """
    if osp.isfile(old_fpath):
        if logger:
            logger.info('copy_file: Attempting to copy file %s to %s...\n'
                        % (old_fpath, new_fpath))
        try:
            shutil.copyfile(old_fpath, new_fpath)
        except IOError as ioer:
            logger.error('copy_file: %s\n' % ioer)
            raise

def update_ident_fpath(session, subject_eid, uuid, delete=False, logger=None):
    """Update the identifier and paths of a subject
    """
    if logger:
        logger.info('update_ident_fpath: processing subject %d...\n' % subject_eid)
    session.execute('SET X identifier %(i)s WHERE X eid %(e)s', {'i': uuid, 'e': subject_eid})
    rset = session.execute('(Any X WHERE X concerns S, S eid %(e)s, '
                           'X is QuestionnaireRun) UNION '
                           '(Any X WHERE S concerned_by X, X is Assessment, '
                            'S eid %(e)s)',
                           {'e': subject_eid}, build_descr=False)
    for concerned_or_assessment_eid in rset:
        concerned_or_assessment_eid = concerned_or_assessment_eid[0]
        if logger:
            logger.info('update_ident_fpath: processing related entity %d\n'
                        % concerned_or_assessment_eid)
        uuid = make_uid() + '_' + unicode(concerned_or_assessment_eid)
        session.execute('SET X identifier %(i)s WHERE X eid %(e)s',
                        {'i': uuid, 'e': concerned_or_assessment_eid})
    rset = session.execute('Any X, F WHERE X concerns S, S eid %(e)s, X filepath F, '
                           'X is IN (Scan, GenomicMeasure)',
                           {'e': subject_eid}, build_descr=False)
    for concerned_eid, concerned_fpath in rset:
        if logger:
            logger.info('update_ident_fpath: processing related entity %d\n' % concerned_eid)
        uuid = make_uid() + '_' + unicode(concerned_eid)
        session.execute('SET X identifier %(i)s WHERE X eid %(e)s', {'i': uuid, 'e': concerned_eid})
        new_filepath = uuid + '_' + osp.basename(concerned_fpath)
        full_fpath = session.entity_from_eid(concerned_eid).full_filepath
        base_fpath = full_fpath.split(concerned_fpath)[0]
        dest_fpath = osp.join(base_fpath, new_filepath)
        copy_file(full_fpath, dest_fpath, logger)
        if delete:
            try:
                os.remove(full_fpath)
            except OSError as oserr:
                if logger:
                    logger.error('update_ident_fpath: %s\n' % oserr)
        session.execute('SET X filepath %(i)s WHERE X eid %(e)s', {'i': new_filepath, 'e': concerned_eid})


def get_ids_uids_from_csv(csv_filename, logger=None):
    try:
        csvf = open(csv_filename, 'r')
    except IOError:
        if logger:
            logger.error('get_ids_uids_from_csv: External UUID CSV file not found: %s\n' % csv_filename)
        raise
    with csvf:
        dialect = csv.Sniffer().sniff(csvf.readline())
        csvf.seek(0)
        return dict(([unicode(x) for x in row] for row in csv.reader(csvf, dialect)))



class BrainomicsRemakeUidCommand(Command):
    """Change subject uids for anonymization.

    <instance>
      the identifier of the instance to anonymize
    """
    name = 'remake-uid'
    arguments = '<instance>'
    min_args = 1
    options = (
        ('log',
         {'short': 'l', 'action': 'store_true', 'default': False,
          'help': 'logging mode: logs all command operations'}),
        ('delete',
         {'short': 'd', 'action': 'store_true', 'default': False,
          'help': ('delete files from the old path, '
                   'after creating the files at the new path')}),
        ('external-uids',
         {'short': 'u', 'type': 'string',
          'help': 'specify external UID file'}),
        )

    def _init_cw_connection(self, appid):
        logger = logging.getLogger('brainomics')
        config = cwconfig.instance_configuration(appid)
        sourcescfg = config.sources()
        config.set_sources_mode(('system',))
        cnx = repo = None
        while cnx is None:
            try:
                login = sourcescfg['admin']['login']
                pwd = sourcescfg['admin']['password']
            except KeyError:
                login, pwd = manager_userpasswd()
            try:
                repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
            except AuthenticationError:
                logger.warning('remake-uuid: wrong user/password')
            else:
                break
        session = repo._get_session(cnx.sessionid)
        return cnx, session

    def run(self, args):
        logger = logging.getLogger('brainomics')
        if len(args) > 0:
            appid = args.pop(0)
            cw_cnx, session = self._init_cw_connection(appid)
            session.set_cnxset()
            log = self.config.log
            delete = self.config.delete
            if self.config.external_uids:
                csv_filename = self.config.external_uids
                ids_uids = get_ids_uids_from_csv(csv_filename, logger)
            if log:
                log_file = logging.FileHandler(appid + '.log')
                logger.addHandler(log_file)
            rset = session.execute('Any X, I WHERE X is Subject, X identifier I', build_descr=False)
            for subject_eid, subject_identifier in rset:
                if not self.config.external_uids:
                    uuid = unicode(make_uid())
                else:
                    try:
                        uuid = ids_uids[subject_identifier]
                    except KeyError:
                        if logger:
                            logger.error('remake-uid: New identifier not found in %s '
                                         'for identifier %s; keeping the old one \n'
                                         % (csv_filename, subject_identifier))
                        session.rollback()
                        raise
                update_ident_fpath(session, subject_eid, uuid, delete, logger)
            session.commit()
        else:
            logger.error("remake-uuid: Please specify Brainomics instance")


CWCTL.register(BrainomicsRemakeUidCommand)
