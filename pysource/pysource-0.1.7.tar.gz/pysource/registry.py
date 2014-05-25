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


import copy

from pysource import arguments
from pysource import request_context


class FunctionHolder(object):

    def __init__(self, function, wrapper, piped):
        self.function = function
        self.wrapper = wrapper
        self.type_spec = arguments.ArgTypeSpec(function)
        self.name = function.__name__
        self.piped = piped

    def run(self, args):
        args = [str(arg) for arg in args]
        parsed_args = self.type_spec.parse(args)
        result = self.wrapper(*parsed_args)
        return str(result) if result is not None else ''

    def to_dict(self):
        return {
            'name': self.name,
            'piped': self.piped
        }

registered = {}


def register(function, wrapper, piped):
    holder = FunctionHolder(function, wrapper, piped)
    registered[holder.name] = holder
    request_context.add_registered(holder)


def run_function(function_name, args):
    if function_name not in registered:
        raise RuntimeError('{0} not registered'.format(function_name))
    holder = registered[function_name]
    if holder.piped and not request_context.piped:
        raise RuntimeError('{0} is a piped function but was called as a '
                           'regular function'.format(function_name))
    if not holder.piped and request_context.piped:
        raise RuntimeError('{0} is a regular function but was called as a '
                           'piped function'.format(function_name))
    return holder.run(args)


def get_registered():
    return copy.copy(registered.values())
