# -*- coding: utf-8 -*-
from setuptools import setup

DESCRIPTION = ("A nifty and interactive command-line tool for efficient"
  "management and execution of commands grouped in hierarchical structures.")

try:
  import pypandoc
  README = pypandoc.convert('README.md', 'rst')
except (ImportError, IOError):
  README = ''

setup(
  name='nifty',
  version='1.6.1',
  provides=['nifty'],
  author='Yanzheng Li',
  author_email='yanzheng819@gmail.com',
  url='https://yanzhengli.github.io/nifty/',
  description='Interactive command-line helper',
  long_description=README or DESCRIPTION,
  classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: Freely Distributable",
        "Topic :: Software Development",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
  ],
  install_requires=['testify'],
  packages=['nifty'],
  entry_points={
    'console_scripts': [
      'nifty = nifty.__main__:main'
    ]
  },
)