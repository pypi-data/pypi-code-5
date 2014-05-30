#!/usr/bin/python
# -*- coding:Utf-8 -*-
from setuptools import setup

try:
    long_description=open("README.md", "r").read(),
except IOError:
    long_description = ""

setup(name='tim',
      version='0.5',
      description='TIM: Timed Iteration Monitor',
      author='Olivier Le Thanh Duong',
      long_description=long_description,
      author_email='olivier@lethanh.be',
      url='https://github.com/olethanh/tim',
      install_requires=[],
      license= 'WTFPL',
      py_modules=["tim"],
      keywords='',
     )
