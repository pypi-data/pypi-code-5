# -*- coding: utf-8 -*-
"""
    sphinxcontrib-dashbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx Dash builder.

    :copyright: Copyright 2014 by shimizukawa@gmail.com.
    :license: BSD, see LICENSE for details.
"""
from __future__ import absolute_import
from __future__ import print_function

import re
import os
import plistlib
import shutil
import sqlite3
import itertools
from collections import namedtuple

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.osutil import ensuredir

from sphinx.errors import ConfigError

from .writer import DashTranslator



# TODO: for Mac
DEFAULT_DOCSET_PATH = os.path.expanduser('~/Library/Application Support/doc2dash/DocSets')


Types = namedtuple('Types',
                   ['CLASS', 'PACKAGE', 'METHOD', 'FUNCTION', 'ATTRIBUTE', 'CONSTANT', 'OPTION'])\
                   ('Class', 'Module',  'Method', 'Function', 'Attribute', 'Constant', 'Option')
                   #('cl',    'Module',  'clm',    'func',     'Attribute', 'clconst',  'option')

_IN_MODULE = '_in_module'

TYPE_MAPPING = [
    (re.compile(r'(.*)\(\S+ method\)$'), Types.METHOD),
    (re.compile(r'(.*)\(.*function\)$'), Types.FUNCTION),
    (re.compile(r'(.*)\(\S+ attribute\)$'), Types.ATTRIBUTE),
    (re.compile(r'(.*)\(\S+ member\)$'), Types.ATTRIBUTE),
    (re.compile(r'(.*)\(class in \S+\)$'), Types.CLASS),
    (re.compile(r'(.*)\(built-in class\)$'), Types.CLASS),
    (re.compile(r'(.*)\(built-in variable\)$'), Types.CONSTANT),
    (re.compile(r'(.*)\(module\)$'), Types.PACKAGE),
    (re.compile(r'(.*)\(opcode\)$'), Types.CONSTANT),
    (re.compile(r'^-(.*)'), Types.OPTION),
    (re.compile(r'(.*)\(in module \S+\)$'), _IN_MODULE),
]


def _get_type_and_name(text):
    '''
    :param str text:
    :return: type, name
    '''
    for mapping in TYPE_MAPPING:
        match = mapping[0].match(text)
        if match:
            name = match.group(1).strip()
            type_ = mapping[1]
            if type_ == _IN_MODULE and name:
                type_ = _guess_type_by_name(name)
            return type_, name
    else:
        return 'Unknown', text


def _guess_type_by_name(name):
    """Module level functions and constants are not distinguishable."""
    if name.endswith('()'):
        return Types.FUNCTION
    else:
        return Types.CONSTANT


class DashBuilder(StandaloneHTMLBuilder):

    name = 'dash'

    def init(self):
        super(DashBuilder, self).init()

        if self.app.config.dash_name is None:
            self.info('Using project name for `dash_name`')
            self.app.config.dash_name = self.app.config.project
        if self.app.config.dash_name.endswith('.docset'):
            self.app.config.dash_name = os.path.splitext(self.app.config.dash_name)[0]

        if self.app.config.dash_icon_file is not None and not self.app.config.dash_icon_file.endswith('.png'):
            raise ConfigError('Please supply a PNG icon for `dash_icon_file`.')

        self.prepare_docset()

    def init_translator_class(self):
        if self.config.dash_translator_class:
            self.translator_class = self.app.import_object(
                self.config.dash_translator_class,
                'dash_translator_class setting')
        else:
            self.translator_class = DashTranslator

    def prepare_docset(self):
        """
        Create boilerplate files & directories.
        """
        self.outrootdir = self.outdir
        self.docsetdir = os.path.join(self.outrootdir, self.app.config.dash_name + '.docset')
        self.outdir = os.path.join(self.docsetdir, 'Contents/Resources/Documents')

        # for HTML output dir
        ensuredir(self.outdir)

        # for sqlite3
        self.sqlite_path = os.path.join(self.docsetdir, 'Contents/Resources/docSet.dsidx')
        if os.path.exists(self.sqlite_path):
            os.remove(self.sqlite_path)

        self.db_conn = sqlite3.connect(self.sqlite_path)
        self.db_conn.row_factory = sqlite3.Row
        self.db_conn.execute(
            'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
            'type TEXT, path TEXT)'
        )
        self.db_conn.commit()

        # for plist
        plist_cfg = {
            'CFBundleIdentifier': self.app.config.dash_name,
            'CFBundleName': self.app.config.dash_name,
            'DocSetPlatformFamily': self.app.config.dash_name.lower(),
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'dashIndexFilePath': 'index.html',
        }
        plistlib.writePlist(
            plist_cfg,
            os.path.join(self.docsetdir, 'Contents/Info.plist')
        )

        # for icon
        if self.app.config.dash_icon_file:
            shutil.copy2(self.app.config.dash_icon_file, os.path.join(self.docsetdir, 'icon.png'))

    def _indexentries(self, name, subname, links):
        typ, name = _get_type_and_name(name)

        if name and subname:
            name += ' - ' + subname

        if name:
            for ismain, link in links:
                yield name, typ, link

    def _iterate_entries(self):
        # yield '<full-name>', '<type>', '<href>'

        ## from domain related indexer
        ## this output is not useful
        # for domain in self.env.domains.itervalues():
        #     for indexcls in domain.indices:
        #         content, collapse = indexcls(domain).generate()
        #         for name, grouptype, page, anchor, extra, qualifier, description in itertools.chain(*[x[1] for x in content]):
        #             yield name, str(indexcls.shortname), '{page}.html#{anchor}'.format(**locals())

        ## from created env index entries
        entries = self.env.create_index(self)
        for entryname, (links, subitems) in itertools.chain(*[x[1] for x in entries]):
            for y in self._indexentries(entryname, None, links):
                yield y
            for subentryname, subentrylinks in subitems:
                for y in self._indexentries(entryname, subentryname, links):
                    yield y

    def handle_finish(self):
        #toc_writer = TocWriter(self.outdir)

        with self.db_conn:
            self.info('Writing docset indexes...')
            for entry in self._iterate_entries():
                self.db_conn.execute(
                    'INSERT INTO searchIndex VALUES (NULL, ?, ?, ?)',
                    entry
                )
                #toc_writer.send(entry)
            self.info('Added {0} index entries.'.format(
                self.db_conn.execute('SELECT COUNT(1) FROM searchIndex')
                       .fetchone()[0]))
            self.info('Adding table of contents meta data...')
            #toc_writer.close()

        # if self.app.config.dash_add_to_docsets:
        #     self.info('Adding to dash...')
        #     os.system('open -a dash "{}"'.format(self.docsetdir)) #TODO for Mac
