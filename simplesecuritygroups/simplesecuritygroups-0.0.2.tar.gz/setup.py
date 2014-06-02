#!/usr/bin/env python
from distutils.core import setup

setup(
    name = "simplesecuritygroups",
    packages = ["simplesecuritygroups"],
    version = "0.0.2",
    description = "Programatic way of creating Cloudformation SecurityGroup Templates",
    author = "Nicholas Johns",
    author_email = "nick.johns@gmail.com",
    url = "https://pypi.python.org/pypi/simplesecuritygroups/",
    install_requires = ["six"],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
