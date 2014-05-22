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

import os
import sys

import docker_registry.tools as tools

requirements_txt = open('./requirements.txt')
requirements = [line for line in requirements_txt]

ver = sys.version_info

if ver[0] == 2:
    if ver[1] <= 6:
        # Python 2.6 requires additional libraries
        requirements.insert(0, 'argparse>=1.2.1')

packages = [
    'docker_registry',
    'docker_registry.tools',
    'docker_registry.tools.dpy',
    'docker_registry.tools.driver']

# Setuptools, this is crap!
p = os.listdir('scaffold/driver')
package_data = []
for f in p:
    if os.path.isfile(os.path.join('scaffold', 'driver', f)):
        package_data.append(os.path.join('..', 'scaffold', 'driver', f))
package_data.append('../scaffold/driver/docker_registry/drivers/*')
package_data.append('../scaffold/driver/docker_registry/__init__.py')
package_data.append('../scaffold/driver/tests/*')

setuptools.setup(
    name=tools.__title__,
    version=tools.__version__,
    author=tools.__author__,
    author_email=tools.__email__,
    maintainer=tools.__maintainer__,
    maintainer_email=tools.__email__,
    url=tools.__url__,
    description=tools.__description__,
    download_url=tools.__download__,
    long_description=open('./README.md').read(),
    keywords=tools.__keywords__,
    namespace_packages=['docker_registry'],
    packages=packages,
    # include_package_data=True,
    package_data={'docker_registry': package_data},
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
    zip_safe=False,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'dpy-driver = docker_registry.tools.driver:main',
            'dpy = docker_registry.tools.dpy:main'
        ]
    },
    install_requires=requirements,
    tests_require=open('./requirements-test.txt').read(),
    extras_require={
        'style': open('./requirements-style.txt').read(),
        'test': open('./requirements-test.txt').read(),
        'full': ('%s\n%s' % (
            open('./requirements-style.txt').read(),
            open('./requirements-test.txt').read())
        )
    }
)
