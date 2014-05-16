#!/usr/bin/env python

from setuptools import setup

setup(name="pysdl2-cffi",
    version = "0.0.1",
    packages = [ 'sdl', '_sdl' ],
    install_requires = [ 'cffi', 'apipkg' ],
    summary = "SDL2 wrapper with cffi",
    license = "BSD",
    author="Daniel Holth",
    author_email="dholth@fastmail.fm")
