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
import sys
from gettext import gettext as _

class ProgramChecker:

    def _checkUser(self):
        user_id  = subprocess.check_output(["id","-u"])
        user_id = user_id.strip()
        if not user_id == "0":
            raise IncorrectUserError

    def _checkPythonVersion(self):
        version = sys.version_info
        major, minor = int(version.major), int(version.minor)
        if major == 2 and minor < 7:
            raise PythonVersionError

    def printError(self, msg):
        print ""
        print msg
        print ""
        sys.exit()

    def check(self):
        try:
            self._checkUser()
        except IncorrectUserError:
            self.printError(_(
                u"ERROR: This program must be run with root user privileges"))
        except PythonVersionError:
            self.printError(_(
u"""ERROR: This program was written for Python 2.7 and you are using an earlier
version."""))


class IncorrectUserError(EnvironmentError):
    """
    """

class PythonVersionError(EnvironmentError):
    """
    """
