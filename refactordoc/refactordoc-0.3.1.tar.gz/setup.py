# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  file: base_doc.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from setuptools import setup
import os
import subprocess

MAJOR = 0
MINOR = 3
MICRO = 1

VERSION = '{0:d}.{1:d}.{2:d}'.format(MAJOR, MINOR, MICRO)
IS_RELEASED = True


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = "Unknown"

    return git_revision


def write_version_py(filename='refactordoc/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM REFACTORDOC SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of refactordoc._version
    # messes up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev = git_version()
    elif os.path.exists('refactordoc/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from refactordoc._version import git_revision as git_rev
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "refactordoc/_version.py and the build "
                              "directory before building.")
    else:
        git_rev = "Unknown"

    if not IS_RELEASED:
        fullversion += '.dev1-' + git_rev[:7]

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))


if __name__ == "__main__":
    write_version_py()
    from refactordoc import __version__

    setup(
        name='refactordoc',
        version=__version__,
        packages=['refactordoc'],
        author="Enthought Ltd",
        author_email="info@enthought.com",
    )
