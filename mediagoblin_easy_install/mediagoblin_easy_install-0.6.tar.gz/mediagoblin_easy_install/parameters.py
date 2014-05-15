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
import argparse
import os
from gettext import gettext as _
from mediagoblin_easy_install.instructions import INSTRUCTIONS

def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=_(
            'A script to help you set up your GMG Mediagoblin server'))
    serving_method = parser.add_mutually_exclusive_group()
    serving_method.add_argument('--locally-served',
        action='store_const', const='locally_served', dest='serving_method')
    serving_method.add_argument('--with-nginx',
        action='store_const', const='with_nginx', dest='serving_method')
    sql_group = parser.add_mutually_exclusive_group()
    sql_group.add_argument('--with-postgresql',
        action='store_const', const='postgresql', dest='sql_database')
    sql_group.add_argument('--with-sqlite',
        action='store_const', const='sqlite', dest='sql_database')

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('--verbose','-v',
        action="count", default=1)
    verbosity.add_argument('--quiet','-q',
        action='store_const', const=0, dest='verbose')

    distribution = parser.add_mutually_exclusive_group()
    distribution.add_argument('--deb',
        action='store_const', const='debian-based', dest='distro')
    distribution.add_argument('--rpm',
        action='store_const', const='redhat-based', dest='distro')

    parser.add_argument('--development',
        action='store_true')

    args = parser.parse_args()

    return args


class InfoHelper:
    """
    The base object which gets input from the user so that they can install
    mediagoblin to their specifications. This class is only meant to be used as
    a base, and the methods are empty to allow for multiple methods of input.
    """

    def __init__(self):
        self.instructions = INSTRUCTIONS


    def _get_database(self):
        """
        Find out what type of SQL database the user wants to use. Either sqlite3
        or postgresql

        :returns string sqldatabase         'sqlite' for sqlite3
                                            'postgresql' for postgresql
        """
        return

    def _get_directory_name(self):
        """
        Find out where the user wants to install the mediagoblin server

        :returns tuple              A tuple of two string, the first being the
                                    path to where mediagoblin will be installed
                                    on this computer, the second being the path
                                    to the directory that the mediagoblin repos-
                                    -itory will be cloned into
        """
        return


    def _get_distribution(self):
        """
        Find out which package manager the user will be using.

        :returns string             Returns a string that should have the value
                                    'debian-based' or 'redhat-based'
        """
        return


    def _get_email(self):
        """
        Find out if the user will be using a custom system email for their serv-
        -er.

        :returns string             The email the user will use as the server
                                    email
        """
        return

    def _get_serving_method(self):
        """
        Finds out how the user would like to serve their website.

        :returns string             A name to reference the differently impleme-
                                    -nted server types
        """
        return

    def getInfoFromUser(self):
        args =  build_argument_parser()
        self.verbose = args.verbose
        serving_method = args.serving_method or self._get_serving_method()
        distro = args.distro or self._get_distribution()
        directory_path, server_name = self._get_directory_name()
        db_type = args.sql_database or self._get_database()
        developing = args.development
        return {'distro':distro, 'directory_path':directory_path,
                'server_name':server_name, 'sql_database':db_type,
                'verbose':self.verbose, 'serving_method':serving_method,
                'for_developing':developing}



class CommandLineHelper(InfoHelper):


    def _get_database(self):
        choice = self._getAnswer(self.instructions['sql_database'])

        sql_database = { '0':'sqlite',
                         '1':'postgresql'}[choice]

        return sql_database


    def _get_directory_name(self):
        # Get and check the actual directory name from the user
        server_name = raw_input(
            self.instructions['directory_name']+"> ")
        server_name = self._checkServername(server_name)
        dir_name = self._checkFilename(server_name)

        # Get and check the local path where the server will be stored.
        responses = ['/srv/<new directory>',
                     '/home/mediagoblin/<new directory>',
                     _('I want to choose a different directory location')]
        choice = self._getAnswer(self.instructions['directory_path'])

        dir_path = {'0':'/srv/',
                    '1':'/home/mediagoblin/',
                    '2':'other'}[choice]

        if dir_path == 'other' : dir_path = raw_input(
            self.instructions['directory_path_other'])

        dir_path = self._checkPath(dir_path)
        dir_name = os.path.join(dir_path, dir_name)

        return dir_name, server_name


    def _get_distribution(self):
        choice = self._getAnswer(self.instructions['linux_distro'])
        distro = {
            '0':'debian-based',
            '1':'redhat-based',
            '2':'invalid' }[choice]

        if distro == 'invalid':
            self._printIfVerbose(_("""
I'm sorry, this script was written assuming that you're using a linux distribut-
-ion based on Debian or Redhat. The script is exiting now.
"""))
            exit()

        return distro


    def _get_email(self):
        """
        Find out if the user will be using a custom system email for their serv-
        -er.
        """
        email = raw_input(instructions['system_email'])
        email = self._checkEmail(email)

        return email

    def _get_serving_method(self):
        """
        Finds out how the user would like to serve their website.

        :returns string             A name to reference the differently impleme-
                                    -nted server types
        """
        choice = self._getAnswer(self.instructions['serving_method'])
        serving_method = {
                '0':'locally_served',
                '1':'with_nginx'}[choice]

        return serving_method


    def _checkServername(self, server_name):
        return server_name

    def _checkFilename(self,filename):
        """
        Checks that a filename given by the user will not cause any errors
        """
        if not filename.endswith('/'): filename += '/'
        return filename


    def _checkPath(self, path):
        """
        Checks that a path given by the user will not cause any errors and that
        the path exists
        """
        if not path.endswith('/'): path += '/'
        return path


    def _checkEmail(self, email):
        """
        Checks that the email given by the user is in a suitable format.
        Not yet implemented.
        """
        return email


    def _getAnswer(self, question_dictionary):
        """
        A simple helper method to get user input from the user in a clear way.

        :param string question      Holds the question which is outputted to the
                                    user.
        :param list responses       A list of all of the possible responses a
                                    user can give.
        """

        question, responses = (question_dictionary['question'],
                               question_dictionary['responses'])
        print question
        options = self._getOptions(responses)
        control = ['q']
        answer = raw_input("> ")

        if answer not in options and answer not in control: answer = None
        while answer is None:
            print _("""
Invalid answer, please enter one of the given responses or press 'q' to quit.
""")
            answer = raw_input("> ")
            if answer not in options and answer not in control: answer = None

        if answer == 'q': exit()

        return answer


    def _getOptions(self, responses):
        """
        A method that prints the options for EasyInstaller._getAnswer
        """
        options = range(0, len(responses))
        for option in options:
            response = responses[option].replace("\n","\n       ")
            option_output = "  {option}    {response}".format(
                option      = str(option),
                response    = response)
            print option_output

        return map(str,options)

