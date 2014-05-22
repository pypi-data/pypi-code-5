# -*- coding: utf-8 -*-
# Copyright (c) 2014 Docker.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
# import colorama
# from collections import deque
import logging
import os
import re
import subprocess

from .. import printer

logger = logging.getLogger(__name__)

description = """Docker python publication helper"""

parser = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    'command', choices=['sanity', 'style', 'test', 'test-all', 'publish'],
    nargs=1, help='Specify what to do')
parser.add_argument('-d', '--dir', help='Path to the module (defaults to cwd)')
# parser.add_argument(
#     '-p', '--pretend', '--dry-run',
#     help='Don\'t actually perform any operation')

global base
global packagename
base = '.'
packagename = ''


def setuptools(*args, **kwargs):
    path = ''
    if 'path' in kwargs:
        path = kwargs['path']
    if not os.path.exists(os.path.join(path or base, 'setup.py')):
        raise Exception('No package in %s' % path)
    args = list(args)
    args.insert(0, 'setup.py')
    args.insert(0, 'python')
    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        cwd=path or base)
    popen.wait()
    output = popen.stdout.read()
    return output.strip()


def git(*args, **kwargs):
    path = ''
    if 'path' in kwargs:
        path = kwargs['path']

    args = list(args)
    args.insert(0, 'git')
    popen = subprocess.Popen(
        args,
        stdout=subprocess.PIPE, cwd=path or base)
    popen.wait()
    output = popen.stdout.read()
    return output.strip()


def gitconfig(key, path=None):
    return git('config', key, path=path)


def flake(path=None):
    try:
        import flake8  # noqa
    except Exception:
        # ensure deps
        popen = subprocess.Popen(
            ('pip', 'install', 'docker-python-dev[style]'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path or base)
        popen.wait()
        if popen.returncode:
            printer.fatal(popen.stderr.read())

    popen = subprocess.Popen(
        ('flake8', '.'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path or base)
    popen.wait()
    output = popen.stdout.read()
    if output:
        printer.fatal(output)
    return


def nose(path=None):
    try:
        import nose  # noqa
    except Exception:
        # ensure deps
        popen = subprocess.Popen(
            ('pip', 'install', 'docker-python-dev[tests]'),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path or base)
        popen.wait()
        if popen.returncode:
            printer.fatal(popen.stderr.read())

    popen = subprocess.Popen(
        ('python', 'setup.py', 'nosetests'),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path or base)
    popen.wait()
    # output = popen.stdout.read()
    outerr = popen.stderr.read()
    if popen.returncode:
        printer.fatal(outerr.decode('utf8'))
    printer.success(outerr.decode('utf8'))
    return outerr.strip()


def getpypi(name, version):
    try:
        import xmlrpclib
    except ImportError:
        import xmlrpc.client as xmlrpclib
    # import pprint
    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    rez = client.package_releases(name)
    if not len(rez):
        printer.warn('That package is not published on pypi it seems.')
    else:
        rez = rez.pop()
        printer.info('Package found on pypi. Versions: %s' % rez)
    if rez == version:
        printer.fatal('What you have here bear the same version as on pypi!')

    # Update register
    setuptools('register')

    # Tag
    git('tag', version)
    git('push', '--follow-tags')

    setuptools('sdist', 'upload')

    printer.info('You should bump your package version NOW.')

    # Stackbrew to be done
    # raw_input()


def publish(name, version):
    # Pypi comes first: check what version is there
    getpypi(name, version)


def main(args=None):
    global base

    args = parser.parse_args(args)
    base = os.getcwd()
    if args.dir:
        base = args.dir

    if args.command[0] == 'sanity':
        auditfiles()
        auditsetup()
    elif args.command[0] == 'style':
        auditstyle()
    elif args.command[0] == 'test':
        nose()
    elif args.command[0] == 'test-all':
        import tox
        tox.cmdline(('-c', os.path.join(base, 'tox.ini')))
    elif args.command[0] == 'publish':
        printer.info('Going to run sanity checks and tests first')
        auditfiles()
        packagename, packageversion = auditsetup()
        auditstyle()
        nose()
        publish(packagename, packageversion)

    exit(0)


def auditstyle():
    output = flake()
    if output:
        output = output.split('\n')
        for line in output:
            # filename, linenb, charnb, message = line.split(':')
            # message = deque(message.strip().split(' '))
            # rule = message.popleft()
            # message = ' '.join(message)
            # printer.warn(' '.join((colorama.Fore.RED, filename,
            # colorama.Fore.BLACK, 'line', linenb)))
            printer.warn(line)

        printer.fatal('Your style is no good! Please fix.')


def auditfiles():
    fl = ['.editorconfig', '.gitignore', '.travis.yml', 'AUTHORS', 'LICENSE',
          'MANIFEST.in', 'README.md', 'requirements.txt', 'setup.cfg',
          'tox.ini']
    for f in fl:
        if not os.path.exists(os.path.join(base, f)):
            printer.warn('You miss a %s file' % f)


def auditsetup():
    name = setuptools('--name')
    version = setuptools('--version')

    if not name:
        printer.fatal('No package name!')
    if not version:
        printer.fatal('No package version!')
    if not setuptools('--fullname'):
        printer.fatal('No package fullname!')

    uname = setuptools('--author')
    umail = setuptools('--author-email')

    maintainername = setuptools('--maintainer')
    maintainermail = setuptools('--maintainer-email')

    contactname = setuptools('--contact')
    contactmail = setuptools('--contact-email')

    if not uname or not maintainername or not contactname:
        printer.fatal('Missing (|maintainer|contact) name!')

    if not umail or not maintainermail or not contactmail:
        printer.fatal('Missing (|maintainer|contact) mail!')

    githubname = gitconfig('github.user')
    # gitkey = gitconfig('user.signingkey')
    # if not gitkey:
    #     printer.fatal(
    #         'No gpg key!' +
    #         ' Please specify one using `git config user.signingkey`')

    gname = gitconfig('user.name')
    gmail = gitconfig('user.email')

    ismaintainer = maintainername == gname
    ismaintainer |= maintainermail == gmail
    ismaintainer |= uname == gname
    ismaintainer |= umail == gmail
    ismaintainer |= contactname == gname
    ismaintainer |= contactmail == gmail
    ismaintainer |= githubname == gname

    if ismaintainer:
        printer.success('You are this package author/maintainer.')
    else:
        printer.warn("""You don\'t seem to be the maintainer of this package
            Disabling publication. You can still override this later on.""")

    giturl = gitconfig('remote.origin.url')

    s = re.compile(':([^/]+)/([^/]+).git$')
    owner, repo = s.findall(giturl)[0]

    url = setuptools('--url')

    if not url == 'https://github.com/%s/%s' % (owner, repo):
        printer.warn('Url (%s) and github repo (%s) don\'t match!' % (
            url,
            'https://github.com/%s/%s' % (owner, repo)
        ))

    license = setuptools('--license')
    if not license:
        printer.fatal('You need a license!')

    desc = setuptools('--description')
    if not desc:
        printer.fatal('You need a description!')

    ldesc = setuptools('--long-description')
    if not ldesc:
        printer.fatal('You need a long description!')

    plat = setuptools('--platforms')
    if not plat:
        printer.warn('You should specify a platform ("Independent")')

    keyw = setuptools('--keywords')
    if not keyw:
        printer.warn('You should specify keywords')

    # classi = setuptools('--classifiers').split('\n')

    return (name, version)

if __name__ == "__main__":
    main()
