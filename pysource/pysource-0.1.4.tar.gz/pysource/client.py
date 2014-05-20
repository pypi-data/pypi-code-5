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


import os
from StringIO import StringIO

import pysource
from pysource import shell
from pysource import handlers


def run_function(function_name, args):
    result = handlers.run_function.remote(name=function_name, args=args)
    return result['result']


def run_piped_function(function_name, args):
    handlers.run_piped_function.remote(name=function_name, args=args)


def list_registered():
    result = handlers.list_registered.remote()
    return result['descriptors']


def update_env():
    result = handlers.update_env.remote(env=os.environ.copy())
    return result['status']


def source_registered(verbose=False):
    return shell.create_shell_functions(list_registered(),
                                        verbose=verbose)


def source_named(function_name, piped=False, verbose=False):
    descriptor = {'name': function_name, 'piped': piped}
    return shell.create_shell_functions([descriptor],
                                        verbose=verbose)


def source_path(file_path, verbose=False):
    if not os.path.exists(file_path):
        raise pysource.error('{0} does not exist'.format(file_path))
    with open(file_path, 'r') as f:
        content = f.read()
    return source_content(content,
                          verbose=verbose)


def source_def(def_content, piped=False, verbose=False):
    content = StringIO()
    content.writelines([
        'import pysource\n',
        '@pysource.function(piped={})\n'.format(piped),
        'def {}'.format(def_content)])
    return source_content(content.getvalue(),
                          verbose=verbose)


def source_content(content, verbose):
    result = handlers.source_register.remote(source_content=content)
    return shell.create_shell_functions(result['descriptors'],
                                        verbose=verbose)
