#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pptable',
    version='0.0.2',
    url='http://github.com/munhitsu/pptable',
    license='MIT',
    author='Mateusz Lapsa-Malawski',
    author_email='m@cr3.io',
    description='pretty prints list of dictionaries as an ascii table',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=True,
    platforms='any',
    install_requires=[
    ],
    classifiers=[
    ],
)
