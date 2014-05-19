
import shutil
from tempfile import mkdtemp

import pytest
import peewee
from vcstools import get_vcs_client

from kez.models import Project, Document, Repository
from kez.utils import evaluate_config_options
from .data import *

pathexists = os.path.exists
pathjoin = os.path.join

def test_vcs_checkout():
    tmp= mkdtemp(prefix="kez-test-")
    git = pathjoin(tmp, '.git')
    assert not pathexists(git)
    client = get_vcs_client("git", tmp)
    client.checkout(URL1)
    assert pathexists(git)
    shutil.rmtree(tmp)

def test_create_project_from_url(db):
    query = list(Project.select())
    assert len(query) == 0
    project = Project.from_url(URL1, name="blog")
    assert project
    assert project.url == URL1
    assert project.vcs == "git"
    assert project.name == "blog"
    assert project.host == "github"
    project.save()
    query = list(Project.select())
    assert len(query) == 1
    assert query[0].url == URL1
    assert query[0].vcs == "git"
    assert query[0].name == "blog"
    assert query[0].host == "github"

def test_empty_and_non_empty_query():
    query = Project.select().where(Project.url=="doesnotexist")
    assert len(list(query)) == 0
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 1

def test_read_project_repository_config(vcs_cache):
    repo = Repository.instance("blog", vcs_cache)
    repo.checkout()
    cfg = repo.get_project_config()
    assert cfg.sections() == ['maths.averagehuman.org']
    assert cfg.get('maths.averagehuman.org', '__doctype__') == 'pelican'
    options, settings = evaluate_config_options(cfg, 'maths.averagehuman.org')
    assert options['doctype'] == 'pelican'
    assert settings['THEME'] == 'theme'

def test_process_project_repository(vcs_cache):
    repo = Repository.instance("blog", vcs_cache)
    repo.checkout()
    assert(len(list(Document.select()))) == 0
    repo.process()
    docs = list(Document.select())
    assert len(docs) == 1
    doc = docs[0]
    assert doc.name == "maths.averagehuman.org"
    assert doc.doctype == "pelican"


def test_delete_project(db):
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 1
    project = query[0]
    assert project.url == URL1
    dq = project.delete()
    assert isinstance(dq, peewee.DeleteQuery)
    dq.execute()
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 0


