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
import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

description = """Docker registry driver development tools"""

parser = argparse.ArgumentParser(description=description,
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    'command', choices=['new'], nargs=1, help='Specify what to do')
parser.add_argument('-d', '--dir', help='Path to the driver (defaults to cwd)')


def gitconfig(key):
    popen = subprocess.Popen(("git", "config", key), stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    return output.strip()


def prompt(desc, default=None):
    if default:
        desc = "%s (default: %s)" % (desc, default)
    return raw_input('%s: ' % desc) or default


def main(args=None):
    args = parser.parse_args(args)

    cur_dir = os.getcwd()

    if args.dir:
        cur_dir = args.dir

    if not os.path.exists(cur_dir):
        logger.debug('Specified directory %s doesn\'t exist, trying to create')
        os.makedirs(cur_dir)

    if not os.path.isdir(cur_dir):
        logger.debug('Specified directory %s is not a directory!')
        raise Exception('Not a folder! %s' % cur_dir)

    driver = {
        'author': {'name': '', 'mail': '', 'nick': ''},
        'name': '',
        'copyright': 'Copyright 2014'
    }

    # if args.command[0] == 'new':
    logger.info('Going to create a new empty driver in directory %s' %
                cur_dir)
    driver['name'] = prompt(
        'You driver name (lowercase, alpha only)', 'my-driver')
    driver['author']['name'] = prompt('Your name', gitconfig('user.name'))
    driver['author']['nick'] = prompt(
        'Your github nick', gitconfig('github.user'))
    driver['author']['mail'] = prompt(
        'Your email', gitconfig('user.email'))
    driver['copyright'] = prompt('Copyright', 'Copyright 2014')

    src = os.path.join(
        os.path.dirname(__file__), '..', '..', '..', 'scaffold', 'driver')
    dest = os.path.join(cur_dir, 'docker-registry-driver-%s' % driver['name'])
    shutil.copytree(
        src,
        dest)

    # Now, move what needs be
    os.rename(
        os.path.join(
            dest, 'docker_registry', 'drivers', '{{driver.name}}.py'),
        os.path.join(
            dest, 'docker_registry', 'drivers', '%s.py' % driver['name']))

    files = []
    files.append(
        os.path.join('docker_registry', 'drivers', '%s.py' % driver['name']))
    files.append('README.md')
    files.append('setup.py')
    files.append('tests/test.py')

    reps = {
        '{{driver.name}}': driver['name'],
        '{{driver.copyright}}': driver['copyright'],
        '{{driver.author.name}}': driver['author']['name'],
        '{{driver.author.mail}}': driver['author']['mail'],
        '{{driver.author.nick}}': driver['author']['nick']
    }

    for key in files:
        src = open(os.path.join(dest, key), 'rb+')
        data = src.read().decode('utf8')
        for k in reps.keys():
            data = data.replace(k, str(reps[k]))

        src.truncate(0)
        src.seek(0)
        src.write(data.encode('utf8'))

if __name__ == "__main__":
    main()
