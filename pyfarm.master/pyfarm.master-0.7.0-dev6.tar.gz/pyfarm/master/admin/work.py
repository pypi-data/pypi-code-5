# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Job
===

Objects and classes for working with the job models.
"""

from pyfarm.master.admin.baseview import SQLModelView
from pyfarm.master.application import SessionMixin
from pyfarm.models.job import Job, JobTag, JobSoftware
from pyfarm.models.task import Task


class JobRolesMixin(object):
    access_roles = ("admin.db.work.job", )


# TODO: !!! add display override for STATE field
class JobView(SessionMixin, JobRolesMixin, SQLModelView):
    model = Job


# TODO: !!! add display override for STATE field
class TaskView(SessionMixin, SQLModelView):
    access_roles = ("admin.db.work.task", )
    model = Task


class JobTagView(SessionMixin, JobRolesMixin, SQLModelView):
    model = JobTag


class JobSoftwareView(SessionMixin, JobRolesMixin, SQLModelView):
    model = JobSoftware
