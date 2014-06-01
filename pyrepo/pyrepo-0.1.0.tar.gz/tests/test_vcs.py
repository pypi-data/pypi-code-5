# -*- coding: utf-8 -*-
"""
    descrc

    :copyright: (c) 2014 by Dalton Hubble
    :license: MIT License, see LICENSE for details.
"""

import unittest
from pyrepo import RepoImporter
from pyrepo import Command
from pyrepo import Host
from pyrepo.commands import git
import shutil
import tempfile
import os
import re

class GitCommandTestCase(unittest.TestCase):

    def setUp(self):
        """
        Setup before each test. Temporary directories must be cleaned
        up when done.
        """
        self.git = git
        self.repo_url = os.path.expanduser("~/sources/test_repo")
        self.target = tempfile.mkdtemp()

    def tearDown(self):
        """Teardown after each test"""
        shutil.rmtree(self.target)

    def test_create(self):
        self.git.clone(self.repo_url, self.target)
        repo_file = os.path.join(self.target, "README.rst")
        self.assertTrue(os.path.isfile(repo_file))
        with open(repo_file) as f:
            self.assertTrue("Version 3" in f.read())

    # def test_update(self):
    #     self.git.update()

    def test_tags(self):
        self.git.clone(self.repo_url, self.target)
        tags = self.git.tag_list(cwd=self.target)
        expected_tags = ["master", "v0.0.2", "v0.0.3"]
        self.assertEqual(set(expected_tags), set(tags))


class RepoImporterTestCase(unittest.TestCase):

    def setUp(self):
        self.importer = RepoImporter()
        pass

    def test_github_import_name(self):
        import_path = "github.com/dghubble/python-role"
        repository = self.importer.resolve(import_path)
        self.assertEqual("git", repository.command.name)
        self.assertEqual("https://github.com/dghubble/python-role", 
            repository.url)

    def test_bitbucket_import_name(self):
        import_path = "bitbucket.org/dghubble/role-template"
        repository = self.importer.resolve(import_path)
        self.assertEqual("git", repository.command.name)
        self.assertEqual("https://bitbucket.org/dghubble/role-template", 
            repository.url)


if __name__ == '__main__':
    unittest.main()





