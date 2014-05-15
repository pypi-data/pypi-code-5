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
from subprocess import CalledProcessError, call
import os
from mediagoblin_easy_install.tasks import (InstallationTasks, 
                                        NginxInstallationTasks)

class ArchiveInstallFramework:
    """
    This is not an InstallationTasks object, this is a virtual class only to be
    used as a second parent to the actual Tasks objects below
    """

    def configure_for_an_archive(self):
        local_config = os.path.join(self.directory_path,
            'mediagoblin_local.ini')
        with file(local_config, 'r') as config_file:
            configuration = config_file.read()
        # TODO: Check if the user wants to enable video and audio media
        plugins = """\
[[mediagoblin.plugins.archivalook]]
[[mediagoblin.plugins.metadata_display]]"""
        configuration += plugins

        index = configuration.find("user_privilege_scheme =")
        end_index = configuration.find("\n", index)
        configuration = (configuration[:index] +
            'user_privilege_scheme = "commenter,reporter"' +
            configuration[end_index:])
        with file(local_config, 'w') as config_file:
            config_file.write(configuration)

    def link_assets(self):
        call(['./bin/gmg', 'assetlink'])

class ArchiveLocalInstallationTasks(InstallationTasks, ArchiveInstallFramework):
    def run(self):
        try:
            self.install_dependencies()
            self.add_gmg_user()
            if self.sql_database == 'postgresql':
                self.setup_postgresql()

            self.mk_mediagoblin_directory()
            self.drop_root_privileges()
            self.install_gmg()
            self.setup_virtual_env()
            self.configure()
            self.configure_for_an_archive()
            self.setup_database()
            self.link_assets()
        except CalledProcessError:
            self._teardown()

class ArchiveNginxInstallationTasks(NginxInstallationTasks,
                                        ArchiveInstallFramework):
    def run(self):
        try:
            self.install_dependencies()
            self.install_nginx_dependencies()
            self.add_gmg_user()
            if self.sql_database == 'postgresql':
                self.setup_postgresql()

            self.mk_mediagoblin_directory()
            self.create_nginx_config_link()
            self.drop_root_privileges()
            self.install_gmg()
            self.setup_virtual_env()
            self.extra_nginx_setup()
            self.configure()
            self.configure_for_an_archive()
            self.setup_database()
            self.create_nginx_config()
            self.create_nginx_run_server_script()
            self.link_assets()
        except CalledProcessError:
            self._teardown()
