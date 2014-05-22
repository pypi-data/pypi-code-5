#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

from apycotlib import Command

from checkers.apycot import BaseChecker
from preprocessors.apycot.distutils import pyversions

class PypiUploader(BaseChecker):
    id = 'pypi.upload'

    options_def = {
        'verbose': {
            'type': 'int', 'default': False,
            'help': 'set verbose mode'
            },
        }

    def run(self, test, path=None):
        """run the distutils 'setup.py register sdist upload' command

        The user running the narval bot must have a properly filled
        .pypirc file
        """
        if path is None:
            path = test.project_path()
        if not exists(join(path, 'setup.py')):
            raise SetupException('No file %s' % abspath(join(path, 'setup.py')))
        python = pyversions(test)[0]
        cmdargs = [python, 'setup.py', 'register', 'sdist', 'upload']
        if not self.options.get('verbose'):
            cmdargs.append('--quiet')
        cmd = Command(self.writer, cmdargs, raises=True, cwd=path)
        cmdstatus = cmd.run()
        if cmdstatus == apycotlib.SUCCESS:
            self.writer.info('uploaded tarball to pypi')
        return cmdstatus

apycotlib.register('checker', PypiUploader)
