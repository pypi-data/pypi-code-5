#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Docker.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__author__ = '{{driver.author.name}}'
__copyright__ = '{{driver.copyright}}'
__credits__ = []

__license__ = 'Apache 2.0'
__version__ = '0.0.1'
__maintainer__ = __author__
__email__ = '{{driver.author.mail}}'
__status__ = 'Production'

__title__ = 'docker-registry-driver-{{driver.name}}'
__build__ = 0x000000

__url__ = 'https://github.com/%s/%s' % ('{{driver.author.nick}}', __title__)
__description__ = 'Docker registry {{driver.name}} driver'
__download__ = 'https://github.com/%s/%s/archive/master.zip' % (
    '{{driver.author.nick}}', __title__)

__keywords__ = 'docker registry driver'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    keywords=__keywords__,
    long_description=open('./README.md').read(),
    download_url=__download__,
    namespace_packages=['docker_registry', 'docker_registry.drivers'],
    packages=['docker_registry', 'docker_registry.drivers'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: Apache Software License'],
    platforms=['Independent'],
    license=open('./LICENSE').read(),
    zip_safe=True,
    test_suite='nose.collector',
    install_requires=open('./requirements.txt').read(),
    tests_require=['docker-python-dev[test]']
)
