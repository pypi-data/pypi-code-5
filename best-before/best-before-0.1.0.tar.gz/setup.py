# -*- coding: utf-8 -*-
"""
best-before

Copyright (c) 2014, Friedrich Paetzke (paetzke@fastmail.fm)
All rights reserved.

"""
from setuptools import find_packages, setup

setup(name='best-before',
      py_modules=['best_before'],
      description='',
      long_description=(open('README.rst').read()),
      version='0.1.0',
      license='BSD',
      author='Friedrich Paetzke',
      author_email='paetzke@fastmail.fm',
      url='http://git.vanneva.com/best-before.git',
      packages=find_packages(exclude=['tests*']),
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ])
