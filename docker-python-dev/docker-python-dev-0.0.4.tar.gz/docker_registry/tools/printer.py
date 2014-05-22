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

# from colorama import Back
import colorama
# from colorama import Style

colorama.init()


def fatal(arg, e=None):
    error(arg)
    if e:
        raise e
    exit(1)


def error(arg):
    print('%s%s' % (colorama.Fore.RED, arg))


def warn(arg):
    print('%s%s' % (colorama.Fore.YELLOW, arg))


def success(arg):
    print('%s%s' % (colorama.Fore.GREEN, arg))


def info(arg):
    print('%s%s' % (colorama.Fore.BLUE, arg))


def debug(arg):
    print('%s%s' % (colorama.Fore.RESET, arg))


def prompt(desc, default=None):
    if default:
        desc = "%s (default: %s)" % (desc, default)
    return raw_input('%s: ' % desc) or default
