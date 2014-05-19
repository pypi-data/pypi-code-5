
import os
import sys
import argparse

from cliff.command import Command
from cliff.lister import Lister

from kez.exceptions import *
from kez.manager import Manager
from kez.models import sqlite_proxy, Project, Document

pathexists = os.path.exists

def args_to_dict(arglist):
    kw = {}
    for arg in arglist:
        k, equals, v = arg.partition('=')
        if not (k and equals and v):
            raise ValueError("invalid parameter %s" % arg)
        kw[k.strip('-').strip()] = v.strip()
    return kw

class ManagerMixin(object):

    @property
    def manager(self):
        try:
            return self._manager
        except AttributeError:
            db_path = self.app.options.data_path
            storage_root = os.path.dirname(db_path)
            self._manager = Manager(sqlite_proxy(db_path), storage_root)
        return self._manager

class BaseCommand(Command, ManagerMixin):
    pass

class BaseLister(Lister, ManagerMixin):
    pass

class List(BaseLister):
    """List all documents in each project"""

    def take_action(self, args):
        def iterobjects():
            for project in sorted(self.manager.list_projects()):
                docs = sorted(project.get_document_set())
                if docs:
                    for doc in docs:
                        yield project.name, doc.name, doc.doctype.upper(), project.url
                else:
                    yield project.name, "<Empty>", "", project.url
        return (
            ('Project', 'Document', 'Type', 'Url'),
            sorted(iterobjects()),
        )

class Add(BaseCommand):
    """Add a new project
    
    Eg. kez add blog git://git@<repo>
    """

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help="the name of the new project",
        )
        parser.add_argument(
            'url',
            help="the url of a code repository containing document sources",
        )
        return parser

    def take_action(self, args):
        try:
            project = self.manager.add_project(args.name, args.url)
        except URLFormatError:
            self.app.stderr.write("Invalid url.\n")
        except ObjectExistsError:
            self.app.stderr.write("That project already exists.\n")
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

class ProjectBaseCommand(BaseCommand):

    def get_parser(self, prog_name):
        parser = super(ProjectBaseCommand, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            help="the name of a registered project",
        )
        return parser

class Build(ProjectBaseCommand):
    """Build project documents
    
    Eg.

    Build all project documents:

        $ kez build phd

    Build one or more specific documents in a project:

        $ kez build phd prelim-findings bibliography

    """

    def get_parser(self, prog_name):
        parser = super(Build, self).get_parser(prog_name)
        parser.add_argument(
            'docs',
            nargs='*',
            help="optionally specify one or many documents to build",
        )
        parser.add_argument(
            '-o',
            '--output-path',
            action='store',
            dest='output_path',
            help="the path to a directory to place the project's built documents",
        )
        return parser

    def take_action(self, args):
        try:
            self.manager.build_project(
                args.project, docnames=args.docs, output_path=args.output_path,
                stdout=self.app.stdout,
            )
        except Project.DoesNotExist:
            self.app.stderr.write("Unknown Project: %s\n" % args.project)
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

class Serve(ProjectBaseCommand):
    """Open a HTML document in a browser
    
    Eg. $ kez serve phd

    """

    def get_parser(self, prog_name):
        parser = super(Serve, self).get_parser(prog_name)
        parser.add_argument(
            'docs',
            nargs='*',
            help="specify one or many documents to display",
        )
        return parser

    def take_action(self, args):
        try:
            self.manager.serve_documents(args.project, ids=args.docs)
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

class Reset(Command):
    """Remove all data
    """

    def take_action(self, args):
        try:
            db_path = self.app.options.data_path
            if pathexists(db_path):
                os.remove(db_path)
                self.app.stdout.write("Database removed.\n")
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

