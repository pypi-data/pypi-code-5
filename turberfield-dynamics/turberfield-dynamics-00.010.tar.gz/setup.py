#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup


try:
    # Includes bzr revsion number
    from turberfield.dynamics.about import version
except ImportError:
    try:
        # For setup.py install
        from turberfield.dynamics import __version__ as version
    except ImportError:
        # For pip installations
        version = str(ast.literal_eval(
            open(os.path.join(os.path.dirname(__file__),
                 "turberfield", "dynamics", "__init__.py"),
                 'r').read().split("=")[-1].strip()))

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.txt"),
               'r').read()

setup(
    name="turberfield-dynamics",
    version=version,
    description="""
A package from the Turberfield project. Provides a simulation framework.
    """,
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://www.assembla.com/spaces/turberfield/messages",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    namespace_packages=["turberfield"],
    packages=[
        "turberfield.dynamics",
        "turberfield.dynamics.test"
    ],
    package_data={
        "turberfield.dynamics": [],
        },
    install_requires=[
        "turberfield-common>=00.004",
        ],
    tests_require=[],
    entry_points={
        "console_scripts": [
        ],
    },
    zip_safe=False
)
