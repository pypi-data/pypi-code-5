#!/usr/bin/python
# GNU MediaGoblin Easy Install Script
# Copyright (C) 2013, 2014 MediaGoblin contributors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mediagoblin_easy_install.plugins.setup_archive.tasks import (
    ArchiveLocalInstallationTasks, ArchiveNginxInstallationTasks)
from mediagoblin_easy_install import _version
from mediagoblin_easy_install.check import ProgramChecker
from mediagoblin_easy_install.parameters import CommandLineHelper


class ArchiveEasyInstallApplication:

    def run(self):
        checker = ProgramChecker()
        checker.check()

        helper = CommandLineHelper()
        kwargs = helper.getInfoFromUser()
        serving_method = kwargs['serving_method']
        del kwargs['serving_method']

        if serving_method == "with_nginx":
            task_list = ArchiveNginxInstallationTasks(**kwargs)
        else:
            task_list = ArchiveLocalInstallationTasks(**kwargs)
        try:
            task_list.run()
        except KeyboardInterrupt:
            print "\nCaught SIGINT Signal... Exiting now."
            task_list._teardown()
