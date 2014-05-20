#!/usr/bin/env python

from setuptools import setup

setup(name="pysdl2-cffi",
    version = "0.1.0",
    packages = [ 'sdl', '_sdl', '_sdl_image' ],
    install_requires = [ 'cffi', 'apipkg' ],
    summary = "SDL2 wrapper with cffi",
    license = "MIT",
    author="Daniel Holth",
    author_email="dholth@fastmail.fm",
    url="https://bitbucket.org/dholth/pysdl2-cffi")
