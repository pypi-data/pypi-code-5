# -*- coding: utf-8 -*-
import glob
import os
import re
import sys

from djinter.utils import grep


def lint_migrations(path):
    results = []
    message = u'Possible import of app models in migration {filename}:\n{matches}'
    match_pattern = re.compile('from .+models import ')
    dont_match_pattern = re.compile('^\s*\#')
    for dirpath, dirnames, files in os.walk(path):
        for filename in glob.glob(os.path.join(dirpath, './migrations/*.py')):
            matches = grep(filename, match_pattern, dont_match_pattern)
            if matches:
                results.append(
                    {
                        'severity': 'critical',
                        'message':  message.format(filename=filename, matches=matches),
                    }
                )
    return results


def lint_project(path):
    results = []
    results.extend(lint_migrations(path))
    return results
