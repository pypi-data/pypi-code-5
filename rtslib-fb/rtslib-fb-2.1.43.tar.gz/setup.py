#! /usr/bin/env python
'''
This file is part of RTSLib.
Copyright (c) 2011-2013 by Datera, Inc

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
'''

from setuptools import setup

setup (
    name = 'rtslib-fb',
    version = '2.1.43',
    description = 'API for Linux kernel SCSI target (aka LIO)',
    license = 'Apache 2.0',
    maintainer = 'Andy Grover',
    maintainer_email = 'agrover@redhat.com',
    url = 'http://github.com/agrover/rtslib-fb',
    packages = ['rtslib'],
    scripts = ['scripts/targetctl'],
    use_2to3 = True,
    )
