#!/usr/bin/env python
from setuptools import setup, find_packages


long_description = '''
Tools abound for single/double/multiple dispatch in python, but most
resort to blatantly magical trickery, like inspecting and
injecting names into lower stack frames, allowing strings to be
passed as code and executed in the dispatchers context, and
other things this package deems silly and/or garbage.
'''
VERSION = (0, 0, 3)
__version__ = '.'.join(str(p) for p in VERSION[0:3]) + ''.join(VERSION[3:])

setup(name='nmmd',
      version='.'.join(map(str, VERSION)),
      packages=find_packages(),
      author='Thom Neale',
      author_email='twneale@gmail.com',
      url='http://github.com/twneale/nmmd',
      description='Tools for Non-Magical Multiple Dispatch',
      long_description=long_description,
      platforms=['any'],
      install_requires=[
          'hercules',
      ],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.4"]
)
