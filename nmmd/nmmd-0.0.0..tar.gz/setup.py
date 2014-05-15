#!/usr/bin/env python
from setuptools import setup, find_packages
from nmmd import VERSION

long_description = '''
Tools abound for single/double/multiple dispatch in python, but most
resort to blatantly magical trickery, like inspecting and
injecting names into lower stack frames, allowing strings to be
passed as code and executed in the dispatchers context, and
other things this package deems silly and/or garbage.
'''

setup(name='nmmd',
      version='.'.join(map(str, VERSION)),
      packages=find_packages(),
      author='Thom Neale',
      author_email='twneale@gmail.com',
      url='http://github.com/twneale/nmmd',
      description='Tools for Non-Magical Multiple Dispatch',
      long_description=long_description,
      platforms=['any'],
)
