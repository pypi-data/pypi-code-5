#!/usr/bin/env python

from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

setup(name="boogs",
      version="0.1",
      py_modules=["boogs"],
      description="Builder objects to construct http requests for the Bugzilla REST API",
      long_description=long_description,
      url="https://github.com/st3fan/boogs",
      author="Stefan Arentz",
      author_email="stefan@arentz.ca")
