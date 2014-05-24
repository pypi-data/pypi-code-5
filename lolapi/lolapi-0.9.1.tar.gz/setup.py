#!/usr/bin/env python
from distutils.core import setup

import lolapi

with open('README.md') as f:
    readme = f.read()
with open('requirements.txt') as f:
    requires = f.read().split('\n')

setup (
    name='lolapi',
    version=lolapi.__version__,
    description='Python wrapper for the League of Legends RESTful API by Riot Games',
    author='Steven Motes',
    author_email='steven.motes@gmail.com',
    license='MIT',
    url='https://github.com/smotes/lolapi',
    py_modules=[
        'lolapi.api', 
        'lolapi.champions', 
        'lolapi.data', 
        'lolapi.games',
        'lolapi.leagues',
        'lolapi.stats',
        'lolapi.summoners',
        'lolapi.teams'
    ],
    platforms=['any'],
    requires=requires
)