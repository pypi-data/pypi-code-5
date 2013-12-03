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

import os

import fixtures
import requests
import testtools
from automationclient.v1_1.devices import Device
from automationclient.v1_1.components import Component
from automationclient.v1_1.services import Service
from automationclient.v1_1.architectures import Architecture
from automationclient.v1_1.profiles import Profile
from automationclient.v1_1.properties import Property
from automationclient.v1_1.zones import Zone
from automationclient.v1_1.tasks import Task
from automationclient.v1_1.roles import Role
from automationclient.v1_1.nodes import Node


class TestCase(testtools.TestCase):
    TEST_REQUEST_BASE = {
        'verify': True,
    }

    def setUp(self):
        super(TestCase, self).setUp()
        if (os.environ.get('OS_STDOUT_CAPTURE') ==
                'True' or os.environ.get('OS_STDOUT_CAPTURE') == '1'):
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if (os.environ.get('OS_STDERR_CAPTURE') ==
                'True' or os.environ.get('OS_STDERR_CAPTURE') == '1'):
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))


class TestResponse(requests.Response):
    """Class used to wrap requests.Response and provide some
       convenience to initialize with a dict.
    """

    def __init__(self, data):
        self._text = None
        super(TestResponse, self)
        if isinstance(data, dict):
            self.status_code = data.get('status_code', None)
            self.headers = data.get('headers', None)
            # Fake the text attribute to streamline Response creation
            self._text = data.get('text', None)
        else:
            self.status_code = data

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def text(self):
        return self._text


def from_manager_to_dict(manager):
    print(type(manager))
    t = Device, Component, Service, Architecture, Profile, Property, Zone, \
        Task, Role, Node
    if isinstance(manager, t):
        final_dict = {}
        for key, value in manager._info.items():
            final_dict.update({key: value})
        return final_dict
    elif isinstance(manager, list):
        final_list = []
        for object_manager in manager:
            if isinstance(object_manager, t):
                dict = {}
                for key, value in object_manager._info.items():
                    dict.update({key: value})
                final_list.append(dict)
        return final_list
