# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement

import sys
assert sys.version_info[0:2] >= (2, 6), "Python 2.6 or higher is required"

from os import walk
from os.path import isfile, join
from setuptools import setup

install_requires = [
    "pyfarm.core", "pyfarm.models",
    "flask-login", "flask-admin>=1.0.7",
    "flask-sqlalchemy", "flask-cache",
    "itsdangerous", "blinker", "flask-testing"]

if sys.version_info[0:2] < (2, 7):
    install_requires.append("simplejson")
    install_requires.append("argparse")

if isfile("README.rst"):
    with open("README.rst", "r") as readme:
        long_description = readme.read()
else:
    long_description = ""


def get_package_data():
    master_root = join("pyfarm", "master")
    packge_data_roots = (
        join("pyfarm", "master", "static"),
        join("pyfarm", "master", "templates"),
        join("pyfarm", "master", "api", "templates"),
        join("pyfarm", "master", "api", "static"))

    output = []
    for top in packge_data_roots:
        for root, dirs, files in walk(top):
            for filename in files:
                output.append(join(root, filename).split(master_root)[-1][1:])

    return output

setup(
    name="pyfarm.master",
    version="0.7.0-dev6",
    packages=[
        "pyfarm",
        "pyfarm.master",
        "pyfarm.master.admin",
        "pyfarm.master.api",
        "pyfarm.master.entrypoints"],
    namespace_packages=["pyfarm"],
    include_package_data=True,
    package_data={"pyfarm.master": get_package_data()},
    entry_points={
        "console_scripts": [
            "pyfarm-dev-dbdata = pyfarm.master.entrypoints.dev:dbdata",
            "pyfarm-master = pyfarm.master.entrypoints.master:run_master"]},
    install_requires=install_requires,
    url="https://github.com/pyfarm/pyfarm-master",
    license="Apache v2.0",
    author="Oliver Palmer",
    author_email="development@pyfarm.net",
    description="Sub-library which contains the code necessary to "
                "communicate with the database via a REST api.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2 :: Only",  # (for now)
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Distributed Computing"])