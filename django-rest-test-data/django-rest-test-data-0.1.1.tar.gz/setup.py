#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys


name = 'django-rest-test-data'
package = 'rest_test_data'
description=('Django app that exposes an API that lets you put the database'
             ' in any (legal) desired state.')
url = 'http://github.com/hogarthww/django-rest-test-data'
author='Hogarth Worldwide Ltd.'
author_email='zonza-devs@hogarthww.com'
license = 'GPLv2'
install_requires=['Django', 'model_mommy']


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(package)}
    print "You probably want to also tag the version now:"
    print "  git tag -a %(version)s -m 'version %(version)s'" % args
    print "  git push --tags"
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires
)
