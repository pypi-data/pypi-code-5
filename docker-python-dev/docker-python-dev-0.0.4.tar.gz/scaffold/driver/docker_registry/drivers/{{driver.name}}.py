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

"""
docker_registry.drivers.{{driver.name}}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bla
"""

# Provides the base class you should extend
from docker_registry.core import driver
# If you are writing a boto driver, you should extend this instead
# from docker_registry.core import boto
# Provides the exceptions you must throw in some cases
from docker_registry.core import exceptions
# Provides the cache set/get decorators
from docker_registry.core import lru


# Boto drivers are like this:
# class Storage(boto.Base):
# Regular drivers are like this:
class Storage(driver.Base):
    # If you want to have an init, its signature must be:
    # def __init__(self, path=None, config=None):
    #     pass

    # Here is you should implement an lru enabled get_content
    @lru.get
    def get_content(self, path):
        raise exceptions.FileNotFoundError()

    # ... and put_content
    @lru.set
    def put_content(self, path, content):
        pass

    # ... and remove
    @lru.remove
    def remove(self, path):
        pass

    # For other methods you need to implement see docker_registry.core.driver
