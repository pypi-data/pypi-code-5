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


class DaemonCommands(object):
    """Daemon related commands"""

    namespace = 'daemon'

    @staticmethod
    def start():
        """start the daemon process"""
        started = daemonizer.start()
        if not started:
            return 'daemon already started'

    @staticmethod
    def stop():
        """stop the daemon process"""
        stopped = daemonizer.stop()
        if stopped:
            return 'daemon stopped'
        else:
            return 'daemon not running'

    @staticmethod
    def restart():
        """restart the daemon process"""
        daemonizer.restart()

    @staticmethod
    def status():
        """check the daemon process status"""
        status, pid = daemonizer.status()
        if status == daemonizer.STATUS_STOPPED:
            return 'daemon is (probably) stopped'
        elif status == daemonizer.STATUS_CORRUPTED:
            if pid:
                return 'daemon pidfile exists but process does not seem ' \
                       'to be running (pid: {0}). you should probably clean ' \
                       'the files in {1} and manually check if there' \
                       ' is a daemon running somewhere'\
                       .format(pid, config.pysource_dir)
            else:
                return 'daemon seems to be in an unstable state. manually ' \
                       'remove the files in {0} and kill leftover daemon ' \
                       'processes (if there are any)'\
                       .format(config.pysource_dir)
        else:
            return 'daemon is (probably) running (pid: {0})'.format(pid)

    @classmethod
    def commands(cls):
        return [cls.start, cls.stop, cls.restart, cls.status]


def list_registered():
    """list all functions currently registered"""
    descriptors = client.list_registered()
    if len(descriptors) == 0:
        yield 'no functions registered'
    else:
        yield 'registered functions:'
        for descriptor in descriptors:
            name = descriptor['name']
            piped = descriptor['piped']
            suffix = ' (piped)' if piped else ''
            yield '{}{}'.format(name, suffix)


def update_env(verbose=False):
    """
    update environment variables at the daemon with the current client
    environment
    """
    status = client.update_env()
    if status != 'updated':
        raise pysource.error('failed updating environment')
    if verbose:
        return 'environment updated'


def source_registered(verbose=False):
    """source all functions currently registered"""
    return client.source_registered(verbose=verbose)


@argh.arg('function_name', help='the name of the function to source')
def source_named(function_name, piped=False, verbose=False):
    """source a function named by the first positional argument"""
    return client.source_named(function_name,
                               piped=piped,
                               verbose=verbose)


@argh.arg('def_content', help='the function definition itself')
def source_def(def_content, piped=False, verbose=False):
    """source an inline function definition"""
    return client.source_def(def_content,
                             piped=piped,
                             verbose=verbose)


@argh.arg('content', help='the code to execute at the daemon')
def source_inline(content, verbose=False):
    """
    execute arbitrary code at the daemon. if code contains function
    definitions, they will be sourced at the client
    """
    return client.source_content(content,
                                 verbose=verbose)


@argh.arg('source_path', help='the path to the file to source')
def source(source_path, verbose=False):
    """source a file by its path"""
    return client.source_path(source_path,
                              verbose=verbose)


@argh.arg('function_name', help='the name of the function to run')
def run(function_name, *args):
    """run the function named by the first positional argument"""
    result = client.run_function(function_name, args)
    if result:
        return result


@argh.arg('function_name', help='the name of the function to run')
def run_piped(function_name, *args):
    """
    run the function named by the first positional argument as a piped
    function
    """
    client.run_piped_function(function_name, args)


def main():
    errors = StringIO()
    parser = argh.ArghParser()
    argh.add_commands(parser, [
        source,
        run,
        run_piped,
        list_registered,
        source_registered,
        source_named,
        source_def,
        source_inline,
        update_env
    ], )
    argh.add_commands(parser,
                      functions=DaemonCommands.commands(),
                      namespace=DaemonCommands.namespace,
                      title=DaemonCommands.__doc__)
    argh.dispatch(parser, completion=False, errors_file=errors)
    if errors.len > 0:
        sys.exit(errors.getvalue().strip())


if __name__ == '__main__':
    main()
