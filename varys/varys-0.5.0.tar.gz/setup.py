#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    fpath = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(fpath):
      return open(fpath).read()
    return ""

setup(name='varys',
      version='0.5.0',
      author='Ben Acland',
      author_email='benacland@gmail.com',
      description='For parsing and reformatting behavioral event logs.',
      license='BSD',
      keywords='behavioral',
      url='https://github.com/beOn/varys',
      install_requires=['scipy','chardet'],
      packages=['varys'],
      long_description=read('README.md'),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
      ],
)