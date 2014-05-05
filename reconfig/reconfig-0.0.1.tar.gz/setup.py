#!/usr/bin/env python
# vim: fileencoding=utf8:et:sw=4:ts=8:sts=4

import os
from setuptools import setup


VERSION = (0, 0, 1, "")

setup(
    name="reconfig",
    description="YAML config file manager with signal-triggered reloading " +
        "and watchable key/value changes",
    py_modules=["reconfig"],
    version=".".join(filter(None, map(str, VERSION))),
    author="Travis Parker",
    author_email="travis.parker@gmail.com",
    url="http://github.com/teepark/reconfig",
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    install_requires=['PyYaml'],
)
