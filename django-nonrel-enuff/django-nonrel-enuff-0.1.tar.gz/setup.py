#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-nonrel-enuff',
    version="0.1",
    author='Steve Yeago',
    author_email='subsume@gmail.com',
    description='Crutch for SQL users',
    url='http://github.com/subsume/django-nonrel-enuff',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
