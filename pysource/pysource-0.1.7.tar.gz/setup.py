# Copyright 2014 Dan Kilman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup

setup(
    name='pysource',
    version='0.1.7',
    author='Dan Kilman',
    author_email='dankilman@gmail.com',
    license='Apache License, Version 2.0',
    packages=['pysource'],
    scripts=['pysource.sh'],
    description='"source" and run python functions in bash',
    zip_safe=False,
    install_requires=[
        'argh',
        'python-daemon'
    ],
    keywords='bash shell source function',
    url='https://github.com/dankilman/pysource',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Unix Shell',
        'Topic :: Software Development',
        'Topic :: System :: Shells',
        'Topic :: System :: System Shells',
        'Topic :: Utilities',
    ]
)
