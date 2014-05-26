#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'shtub',
          version = '0.3.6',
          description = '''shtub - shell command stub''',
          long_description = '''''',
          author = "Alexander Metzner, Michael Gruber, Maximilien Riehl, Marcel Wolf, Udo Juettner",
          author_email = "alexander.metzner@gmail.com, aelgru@gmail.com, maximilien.riehl@gmail.com, marcel.wolf@immobilienscout24.de, udo.juettner@gmail.com",
          license = 'GNU GPL v3',
          url = 'https://github.com/yadt/shtub',
          scripts = [],
          packages = ['shtub', 'shtub.verification'],
          py_modules = [],
          classifiers = ['Development Status :: 3 - Alpha', 'Programming Language :: Python'],
             #  data files
             # package data
          
          
          zip_safe=True
    )
