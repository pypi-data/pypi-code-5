# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    long_description = readme_file.read()

setup(name='uncatchable-exception',
      py_modules=['uncatchable_exception'],
      description='An exception class which is not catchable when it was raised.',
      long_description=long_description,
      version='0.1.2',
      license='BSD',
      author='Benjamin Hedrich',
      author_email='benjamin.hedrich@pagenotfound.de',
      url='https://github.com/bh/uncatchable-exception',
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
      ]
)
