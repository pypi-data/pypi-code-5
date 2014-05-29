#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with Mocki. If not, see <http://www.gnu.org/licenses/>.
#

import setuptools


def import_version():
    with open('version', 'r') as version_file:
        return version_file.read().strip()


def import_long_description():
    with open('README.rst', 'r') as long_description_file:
        return long_description_file.read()


setuptools.setup(
    name='Mocki',

    version=import_version(),

    description='An easy-to-use but full featured mocking library for Python.',
    long_description=import_long_description(),

    url='https://launchpad.net/mocki',

    author='Olivier Kozak',
    author_email='olivier.kozak@gmail.com',

    license='GNU LGPL v3',

    packages=['mocki'],

    install_requires=['inflection'],
)
