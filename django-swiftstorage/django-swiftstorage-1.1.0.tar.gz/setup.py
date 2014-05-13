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

from setuptools import setup

TEST_REQUIREMENTS = [
    'mocker',
    'python-keystoneclient==0.2.2',
    'python-swiftclient==1.2.0',
    'django==1.5.5'
]


setup(
    name='django-swiftstorage',
    version='1.1.0',
    author='Mike Heald',
    author_email='mike.heald@canonical.com',
    maintainer='David Murphy',
    maintainer_email='david.murphy@canonical.com',
    url='http://launchpad.net/django-swiftstorage/',
    description='Django swiftstorage for Swift API',
    test_suite='swiftstorage.tests',
    tests_require=TEST_REQUIREMENTS,
    packages=['swiftstorage'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
    ],
)
