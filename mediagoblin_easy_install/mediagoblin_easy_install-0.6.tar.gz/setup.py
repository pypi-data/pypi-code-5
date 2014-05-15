# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
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

from setuptools import setup, find_packages
import os, re

READMEFILE = "README.txt"
VERSIONFILE = os.path.join("mediagoblin_easy_install", "_version.py")
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"


def get_version():
    verstrline = open(VERSIONFILE, "rt").read()
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." %
                           VERSIONFILE)

setup(
    name="mediagoblin_easy_install",
    version=get_version(),
    packages=find_packages(),
    include_package_data = True,
    # scripts and dependencies
    install_requires=[
        'setuptools',
        'argparse',
    ],
    license='AGPLv3',
    author='Free Software Foundation and contributors',
    author_email='natalie.foust.pilcher@gmail.com',
    url="http://mediagoblin.org/",
    long_description=open(READMEFILE).read(),
    )
