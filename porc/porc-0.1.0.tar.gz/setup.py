#!/usr/bin/env python

from setuptools import setup

setup(name='porc',
      version='0.1.0',
      description='Asynchronous Orchestrate.io Interface',
      author='Max Thayer',
      author_email='max@orchestrate.io',
      url='https://github.com/orchestrate-io/porc',
      packages=['porc'],
      license='MIT',
      install_requires=[
          'requests-futures==0.9.4',
          'vcrpy==0.7.0'
      ],
      test_suite="tests",
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          # TODO Python 3 support
          # 'Programming Language :: Python :: 3',
          # 'Programming Language :: Python :: 3.2',
          # 'Programming Language :: Python :: 3.3'
      ],
      )
