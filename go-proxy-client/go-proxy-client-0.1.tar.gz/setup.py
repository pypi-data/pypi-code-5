#!/usr/bin/env python
from setuptools import setup

setup(name='go-proxy-client',
      version='0.1',
      description='Handler for urllib2 to use a go-proxy instance as proxy server',
      maintainer='Stefan Richter',
      maintainer_email='stefan@02strich.de',
      packages=['go_gae_proxy'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.4',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.1',
      ],
      use_2to3=True,
      )
