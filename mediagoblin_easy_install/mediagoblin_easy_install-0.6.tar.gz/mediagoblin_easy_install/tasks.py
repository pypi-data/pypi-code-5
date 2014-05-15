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
import subprocess
from subprocess import CalledProcessError
import pwd
import os
from grp import getgrnam
from gettext import gettext as _

from mediagoblin_easy_install.configs import get_nginx_configuration
from mediagoblin_easy_install.check import ProgramChecker

class InstallationTasks:
    """
    An object that holds all the necessary code to help a user deploy a GMG
    instance. The primary code is held in the InstallationTasks.run method and
    all of the other methods are helper methods to make the code clearer.

    This script only installs mediagoblin as a local server to be viewed on
    localhost. Because it's a very basic script, other more specific installs
    can likely inherit from this class.

    To make a more specific install script create a class that inherits from
    this one, add your new tasks as methods and override the
    InstallationTasks.run method to include the new tasks.
    """


    def __init__(self, distro, directory_path, server_name,
            sql_database, for_developing, verbose):
        """
        :param distro   :type string        A string representing what type of
                                            linux distro you are using, debian-
                                            based or redhat-based. Proper values
                                            are 'debian-based' or 'redhat-based'
        :param directory_path :type string  A string showing the path to your
                                            new mediagoblin install.
        :param server_name  :type string    A string representing your server's
                                            domain name
        :param sql_database :type string    A string representing which type of
                                            sql database you are using. Proper
                                            values are currently 'sqlite' for
                                            sqlite3 and 'postgresql' for
                                            postgresql
        :param for_developing :type bool    A boolean value representing whether
                                            this install will be for development
                                            on GMG or just for use.
        :param verbose :type int            An integer describing how verbose
                                            the user would like the output to be
        """
        self.distro = distro
        self.directory_path = directory_path
        self.server_name = server_name
        self.sql_database = sql_database
        self.for_developing = for_developing
        self.verbose = verbose

        self.createdFiles = []
        self.createdDirectories = []


    def _printIfVerbose(self,output,verbosity=1):
        """
        Prints the output to the stdout if the process is being run in a verbose
        enough mode
        :param output :type string          The output that will be sent to the
                                            user.
        :param verbosity :type int          The amount of verbosity that is req-
                                            -uired by the user's commandline
                                            choices for this message to be shown
        """
        if self.verbose >= verbosity:
            print output

    def _sys_user_exists(self, username):
        """
        A helper function that confirms that a given user exists in a linux
        system
        """
        try:
            pwd.getpwnam(username)
            return True
        except KeyError:
            return False

    def _cd(self,directory):
        """
        Change the directory the process is running in
        """
        try:
            subprocess.os.chdir(self.directory_path)
            self._printIfVerbose(
                _("Changed directory to {directory_path}").format(
                    directory_path=directory), 2)
        except OSError:
            self._printIfVerbose(_("""Could not access {directory_path}, was the
directory not created correctly?""").format(
                directory_path=directory), 0)

    def _teardown(self):
        """
        If installation fails, be sure to delete the files that were created.
        If an error happens after root privileges have been dropped, many files
        will persist, so it's important to catch errors early. In this case, let
        the user know what files have been created.
        """
        successes, failures = [], []

        self._printIfVerbose(_(u"--Exiting program, cleaning up unused files"))
        for createdFile in self.createdFiles:
            try:
                subprocess.check_call(['rm',createdFile])
                successes.append(createdFile)
            except:
                failures.append(createdFile)

        for createdDirectory in self.createdDirectories:
            try:
                subprocess.check_call(['rm','-r',createdDirectory])
                successes.append(createdDirectory)
            except:
                failures.append(createdDirectory)

        success_list = "\n    ".join(successes)
        failure_list = "\n    ".join(failures)
        if len(successes) > 0:
            self._printIfVerbose(
                _(u"""Successfully deleted files:
    {success_list}""".format(
                    success_list = success_list)), 2)

        if len(failures) > 0:
            self._printIfVerbose(
                _(u"""Program could not delete files:
    {failure_list}""".format(
                    failure_list=failure_list)))
        exit(1)

    def install_dependencies(self):
        self._printIfVerbose("Installing mediagoblin dependencies...")
        try:
            if self.distro == 'debian-based':
                subprocess.check_call(['apt-get', 'install',
                    'git-core', 'python', 'python-dev', 'python-lxml',
                    'python-imaging', 'python-virtualenv'])

            elif self.distro == 'redhat-based':
                subprocess.check_call(['yum', 'install',
                    'python-paste-deploy', 'python-paste-script', 'git-core',
                    'python', 'python-devel', 'python-lxml', 'python-imaging',
                    'python-virtualenv'])
        except CalledProcessError:
            self._printIfVerbose(
u'ERROR: Could not properly install dependencies.', 0)
            self._printIfVerbose(
u"""Check your internet connection, and confirm that you have updated your
software sources (ie. `apt-get update` or `yum update`) recently.""")
            raise


    def add_gmg_user(self):
        self._printIfVerbose("Trying to create user `mediagoblin`...")
        if not self._sys_user_exists('mediagoblin'):
            subprocess.call(['adduser', '--system', '--group',
                    'mediagoblin'])
            self._printIfVerbose("mediagoblin user created successfully")
        else:
            self._printIfVerbose(_(
                "User mediagoblin already exists."))


    def setup_postgresql(self):
        self._printIfVerbose(_(
            "Creating new database user for mediagoblin..."))
        subprocess.call(['sudo','-u','postgres','createuser',
            '--no-createdb', '--no-createrole', '--no-superuser',
            'mediagoblin'])
        self._printIfVerbose(_(
            "Database user mediagoblin created."))
        self._printIfVerbose(_(
            "Creating new sql database for mediagoblin..."))
        subprocess.call(['sudo', '-u', 'postgres',
            'createdb', '-E', 'UNICODE',
            '-O', 'mediagoblin', 'mediagoblin'])
        self._printIfVerbose(_(
            "New sql database created."))

    def mk_mediagoblin_directory(self):
        if os.path.exists(self.directory_path):
            self._printIfVerbose(_(
                "Directory {directory} already exists.".format(
                    directory=self.directory_path)))
        else:
            self._printIfVerbose(_("Creating directory {directory}...").format(
                directory=self.directory_path))
            subprocess.call(['mkdir', '-p', self.directory_path])
            subprocess.call(['chown','-hR',
                'mediagoblin:mediagoblin',
                self.directory_path])
            self._printIfVerbose(_("Directory {directory} created.").format(
                directory=self.directory_path))
            self.createdDirectories.append(self.directory_path)

        self._cd(self.directory_path)

    def create_nginx_config_link(self):
        config_filename = "{server_name}.conf".format(
            server_name = self.server_name)
        link_location = os.path.join(
            '/etc/nginx/sites-enabled/', config_filename)
        nginx_config = os.path.join(self.directory_path, "nginx.conf")
        try:
            subprocess.check_call(['ln','-s',
                nginx_config, link_location])
            self.createdFiles.append(link_location)
        except CalledProcessError:
            self._printIfVerbose(
_(u"ERROR: Could not create nginx configuration in /etc/nginx/"))
            self._printIfVerbose(
_(u"""Check to make sure that a file called \
/etc/nginx/site-enabled/{config_filename} does not already exist.""".format(config_filename=config_filename)
), verbosity=2)
            raise

    def drop_root_privileges(self):
        """
        Drops privileges of the process down to 'mediagoblin'. Until this method
        is run, the program should be running as 'root'
        """
        gmg_uid = int(subprocess.check_output(['id','-u','mediagoblin']))
        gmg_gid = getgrnam('mediagoblin').gr_gid
        subprocess.os.setgid(gmg_gid)
        subprocess.os.setuid(gmg_uid)
        self._printIfVerbose(
_(u"Process running as user #{uid}").format(uid=subprocess.os.getuid()),
        verbosity = 2)
        self._printIfVerbose(
_(u"Process running as group #{gid}").format(gid=subprocess.os.getgid()),
        verbosity = 2)

    def install_gmg(self):
        self._printIfVerbose("Getting mediagoblin from git repository...")
        try:
            if self.for_developing:
                subprocess.check_call([ 'git', 'clone',
                    'git://gitorious.org/mediagoblin/mediagoblin.git',
                    self.directory_path])
            else:
                subprocess.check_call(['git','init'])
                subprocess.check_call([ 'git', 'pull',
                    'git://gitorious.org/mediagoblin/mediagoblin.git',
                    'master'])
            self._cd(self.directory_path)
            subprocess.check_call(['git','submodule','init'])
            subprocess.check_call(['git','submodule','update'])
            self._printIfVerbose("Cloned mediagoblin repository successfully.")
        except:
            self._printIfVerbose(
u"""ERROR: Could not properly clone from the mediagoblin repository""", 0)
            self._printIfVerbose(u"Check your internet connection.",1)
            raise

    def setup_virtual_env(self):
        self._printIfVerbose(
            _(u"Setting up a virtual environment inside of {dir}").format(
                dir=self.directory_path))
        self._cd(self.directory_path)
        try:
            subprocess.check_call(['virtualenv','--system-site-packages',
                self.directory_path])
        except CalledProcessError:
            subprocess.call(['virtualenv', '.'])
        subprocess.call(['./bin/python',
            'setup.py', 'develop'], cwd = self.directory_path)

    def configure(self):
        config_path = os.path.join(self.directory_path, 'mediagoblin.ini')
        local_config_path = os.path.join(self.directory_path,
            'mediagoblin_local.ini')

        with file(config_path,'r') as config_file:
            configuration = config_file.read()
        if self.sql_database == 'postgresql':
            index = configuration.find(
                '# sql_engine =')
            end_index = configuration.find('\n',index)
            sql_config ='sql_engine = {sqldb}:///mediagoblin'.format(
                sqldb=self.sql_database)
            configuration = (
                configuration[:index] + sql_config + configuration[end_index:])
        with file(local_config_path,'w') as local_config_file:
            local_config_file.write(configuration)


    def setup_database(self):
        subprocess.call(["./bin/gmg", "dbupdate"],
            cwd = self.directory_path)
        self._printIfVerbose(_("Database set up successfully!"))


    def create_nginx_config(self):
        config_filename = "{server_name}.conf".format(
            server_name = self.server_name)
        configuration = get_nginx_configuration(
            self.server_name, self.directory_path)
        nginx_config = os.path.join(self.directory_path, config_filename)
        with file(nginx_config,'w') as config_file:
            config_file.write(configuration)


    def run(self):
        """
        The method that does all the work of the InstallationTasks classes.
        Runs each task one after the other. Childeren of this class should
        replace this method with a new tasklist.
        """
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
            self.setup_database()
        except CalledProcessError:
            self._teardown()


class NginxInstallationTasks(InstallationTasks):

    def install_nginx_dependencies(self):
        self._printIfVerbose("Installing nginx and nginx dependencies...")
        try:
            if self.distro == 'debian-based':
                subprocess.check_call(['apt-get', 'install', 'nginx-full'])

            elif self.distro == 'redhat-based':
                subprocess.check_call(['yum', 'install', 'nginx-full'])
        except CalledProcessError:
            self._printIfVerbose(
u'ERROR: Could not properly install dependencies.', 0)
            self._printIfVerbose(
u"""Check your internet connection, and confirm that you have updated your
software sources (ie. `apt-get update` or `yum update`) recently.""")
            raise

    def create_nginx_config_link(self):
        config_filename = "{server_name}.conf".format(
            server_name = self.server_name)
        link_location = os.path.join(
            '/etc/nginx/sites-enabled/', config_filename)
        nginx_config = os.path.join(self.directory_path, "nginx.conf")
        try:
            subprocess.check_call(['ln','-s',
                nginx_config, link_location])
            self.createdFiles.append(link_location)
        except CalledProcessError:
            self._printIfVerbose(
_(u"ERROR: Could not create nginx configuration in /etc/nginx/"))
            self._printIfVerbose(_(
u"Check to make sure that {link} does not already exist.".format(
                    link=link_location)), verbosity=2)
            raise

    def extra_nginx_setup(self):
        subprocess.call([
            './bin/pip', 'install', 'flup'], cwd = self.directory_path)

    def create_nginx_config(self):
        config_filename = "nginx.conf"
        configuration = get_nginx_configuration(
            self.server_name, self.directory_path)
        nginx_config = os.path.join(self.directory_path, config_filename)
        with file(nginx_config,'w') as config_file:
            config_file.write(configuration)

    def create_nginx_run_server_script(self):
        script_path = os.path.join(self.directory_path, "run_nginx_server.sh")
        contents = """#!/bin/sh
./lazyserver.sh --server-name=fcgi fcgi_host=127.0.0.1 fcgi_port=26543
"""
        with file(script_path,'w') as server_script:
            server_script.write(contents)

        subprocess.call(['chmod','755', script_path])


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
            self.setup_database()
            self.create_nginx_config()
            self.create_nginx_run_server_script()
        except CalledProcessError:
            self._teardown()
