# -*- coding: utf-8 -*-

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Axe",
    version="0.0.1a",
    author="Ju Lin",
    author_email="soasme@gmail.com",
    description="Decorator for retrying exec a method",
    license="MIT License",
    keywords="Web frameword",
    url="https://github.com/soasme/axe",
    packages=['axe'],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
