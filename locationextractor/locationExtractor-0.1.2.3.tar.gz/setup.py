#!/usr/bin/env python

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup


setup(name='locationExtractor',
      version='0.1.2.3',
      license='MIT',
      description='Searches location info from source. Tokenizes source and finds appropriate country',
      long_description=open('README.md').read(),
      url='https://github.com/fatihsucu/locationExtractor',
      author='Fatih Sucu',
      author_email='fatihsucu0@gmail.com',
      maintainer='Mustafa Atik',
      maintainer_email='muatik@gmail.com',
      packages=['locationExtractor'],
      package_data={'locationExtractor': ['*']},
      platforms='any')