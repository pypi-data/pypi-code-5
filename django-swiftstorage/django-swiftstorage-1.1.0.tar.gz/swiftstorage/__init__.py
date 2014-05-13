# This file is part of django-swiftstorage.
# Copyright 2014 Canonical Ltd.

# django-swiftstorage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
An interface to the python-swiftclient api through Django.
"""

__version_info__ = {
    'major': 1,
    'minor': 1,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 1
}


def get_version():
    vers = ["{major}.{minor}".format(**__version_info__)]

    if __version_info__["micro"]:
        vers.append(".{micro}".format(**__version_info__))
    if __version_info__["releaselevel"] != "final":
        vers.append("{releaselevel}{serial}".format(**__version_info__))
    return "".join(vers)

__version__ = get_version()
