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
import functools
import threading
import argh

remote_call_handlers = {}


def _remote_wrapper(func, piped):
    request_type = func.__name__

    def remote(**kwargs):
        # import here to avoid cyclic dependencies
        if piped:
            from pysource.transport import do_piped_client_request \
                as do_client_request
        else:
            from pysource.transport import do_regular_client_request \
                as do_client_request
        return do_client_request(request_type, kwargs)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    remote_call_handlers[request_type] = wrapper
    wrapper.remote = remote
    return wrapper


def piped_remote_call(func):
    return _remote_wrapper(func, piped=True)


def remote_call(func):
    return _remote_wrapper(func, piped=False)


class RequestContext(threading.local):

    def __init__(self):
        super(RequestContext, self).__init__(self)
        self.registered = []
        self.piped = False
        self.stdin = None
        self.stdout = None

    def add_registered(self, function_holder):
        self.registered.append(function_holder)
request_context = RequestContext()


class RequestContextOut(object):

    @staticmethod
    def write(data):
        if request_context.stdout is None:
            raise RuntimeError('Not running within a piped request context')
        request_context.stdout.write(data)
stdout = RequestContextOut()


class RequestContextIn(object):

    @staticmethod
    def read(length=0, blocking=True):
        if request_context.stdin is None:
            raise RuntimeError('Not running within a piped request context')
        return request_context.stdin.read(length, blocking)
stdin = RequestContextIn()


class SugaredEnviron(os._Environ):

    def __getattr__(self, item):
        return self.get(item)
env = SugaredEnviron(os.environ.data)


def function(func=None, piped=False):
    # import here to avoid cyclic dependencies
    from pysource import registry
    if func is not None:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        registry.register(func, wrapper, piped)
        return wrapper
    else:
        def partial_wrapper(fn):
            return function(fn, piped=piped)
        return partial_wrapper


class error(argh.CommandError):
    pass
