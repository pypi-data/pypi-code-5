#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='sleekdigda',
    version='0.1.0',
    description='XEP-Digda - SleekXMPP plugin',
    long_description=open('README.md').read(),
    author='Optiflows R&D',
    author_email='rand@optiflows.com',
    packages=find_packages(),
    install_requires=[
        'sleekxmpp>=1.2.0,<1.3.0',
    ],
)
