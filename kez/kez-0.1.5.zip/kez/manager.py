
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError

from .models import Project, Document, Repository
from .utils import ensure_dir, parse_vcs_url
from .exceptions import *

class Manager(object):

    def __init__(self, database, storage_root):
        self.db = database
        self.vcs_cache = os.path.join(storage_root, '__VCS__')
        self.build_cache = os.path.join(storage_root, '__BUILD__')
        ensure_dir(self.vcs_cache)

    def _get_project_repo(self, project):
        return Repository(project, self.vcs_cache)

    def add_project(self, name, url):
        try:
            Project.get(Project.url == url)
        except Project.DoesNotExist:
            pass
        else:
            raise ObjectExistsError(url)
        try:
            Project.get(Project.name == name)
        except Project.DoesNotExist:
            pass
        else:
            raise ObjectExistsError(name)
        # create a new Project instance
        project = Project.from_url(url, name=name)
        # checkout project repo and ensure a valid config file before saving
        repo = project.get_repo_object(self.vcs_cache)
        repo.checkout()
        repo.get_project_config()
        # save and return project
        project.save()
        return project

    def list_projects(self):
        return list(Project.select())

    def delete_project(self, name):
        q = Project.delete().where(Project.name==name)
        return q.execute()

    def add_s3_credentials(self, name=None):
        pass

    def update_project(self, name):
        pass

    def build_project(self, project, docnames=None, output_path=None, stdout=sys.stdout):
        """
        Build all project documents OR, if docnames are given, one or more specific documents.

        The `docnames` parameter can be the actual name of a document or, for UI convenience,
        the 1-based index of the document in the list of all project documents.
        """
        docnames = docnames or []
        output_path = output_path or self.build_cache
        repo = Repository.instance(project, self.vcs_cache)
        repo.checkout()
        docs = Project.filter_docset(project, repo.process(), docnames)
        for d in docs:
            stdout.write("***** STARTED BUILDING: %s *****\n" % d)
            d.build(dstroot=output_path)
            stdout.write("***** FINISHED: %s *****\n" % d)
        return docs

    def serve_documents(self, projectname, ids=None):
        project = Project.get(Project.name == projectname)
        docs = project.get_document_set(ids)
        import webbrowser as wb
        for doc in docs:
            page = None
            if doc:
                page = doc.get_html_index()
            if not page:
                raise NoDocumentIndexError("Not found - index.html for '%s'" % doc)
            wb.open(r'file:///' + page)

