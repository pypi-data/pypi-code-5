#!/usr/bin/env python
from distutils.core import setup

import lolapi

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
        'lolapi.common',
        'lolapi.data', 
        'lolapi.exceptions',
        'lolapi.games',
        'lolapi.leagues',
        'lolapi.stats',
        'lolapi.summoners',
        'lolapi.teams'
    ],
    platforms=['any'],
    requires='requests',
)