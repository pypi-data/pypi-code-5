# Copyright 2014 Dan Kilman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from StringIO import StringIO

import argh

import pysource
from pysource import daemonizer
from pysource import client
from pysource import config


def daemon(action):
    if action == 'start':
        started = daemonizer.start()
        if not started:
            return 'Daemon already started'
    elif action == 'stop':
        stopped = daemonizer.stop()
        if stopped:
            return 'Daemon stopped'
        else:
            return 'Daemon not running'
    elif action == 'restart':
        daemonizer.restart()
    elif action == 'status':
        status, pid = daemonizer.status()
        if status == daemonizer.STATUS_STOPPED:
            return 'Daemon is (probably) stopped'
        elif status == daemonizer.STATUS_CORRUPTED:
            if pid:
                return 'Daemon pidfile exists but process does not seem ' \
                       'to be running (pid: {0}). You should probably clean ' \
                       'the files in {1} and manually check if there' \
                       ' is a daemon running somewhere'\
                       .format(pid, config.pysource_dir)
            else:
                return 'Daemon seems to be in an unstable state. Manually ' \
                       'remove the files in {0} and kill leftover daemon ' \
                       'processes (if there are any)'\
                       .format(config.pysource_dir)
        else:
            return 'Daemon is (probably) running (pid: {0})'.format(pid)
    else:
        raise pysource.error('unrecognized action: {0} '
                             '[valid: start, stop, restart, status]'
                             .format(action))


def list_registered():
    descriptors = client.list_registered()
    if len(descriptors) == 0:
        yield 'No functions registered'
    else:
        yield 'Registered functions:'
        for descriptor in descriptors:
            name = descriptor['name']
            piped = descriptor['piped']
            suffix = ' (piped)' if piped else ''
            yield '{}{}'.format(name, suffix)


def update_env(verbose=False):
    status = client.update_env()
    if status == 'updated' and verbose:
        return 'Environment updated'
    else:
        raise pysource.error('Failed updating environment')


def source_registered(verbose=False):
    return client.source_registered(verbose=verbose)


def source_named(function_name, piped=False, verbose=False):
    return client.source_named(function_name,
                               piped=piped,
                               verbose=verbose)


def source_def(def_content, piped=False, verbose=False):
    return client.source_def(def_content,
                             piped=piped,
                             verbose=verbose)


def source_inline(content, verbose=False):
    return client.source_content(content,
                                 verbose=verbose)


def source(source_path, verbose=False):
    return client.source_path(source_path,
                              verbose=verbose)


def run(function_name, *args):
    result = client.run_function(function_name, args)
    if result:
        return result


def run_piped(function_name, *args):
    client.run_piped_function(function_name, args)


def main():
    errors = StringIO()
    argh.dispatch_commands([
        daemon,
        source,
        run,
        run_piped,
        list_registered,
        source_registered,
        source_named,
        source_def,
        source_inline,
        update_env
    ], completion=False, errors_file=errors)
    if errors.len > 0:
        sys.exit(errors.getvalue().strip())


if __name__ == '__main__':
    main()
