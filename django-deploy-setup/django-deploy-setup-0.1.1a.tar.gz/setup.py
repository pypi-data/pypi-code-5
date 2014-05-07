# coding: utf-8
from __future__ import unicode_literals

from setuptools import setup, find_packages
from django_deploy import __version__

setup(
    name='django-deploy-setup',
    version=__version__,
    license='MIT',

    author='Tomáš Ehrlich',
    author_email='tomas.ehrlich@gmail.com',

    description='Deployment tools for django projects',
    long_description=open('README.md').read(),
    url='https://github.com/elvard/django-deploy',

    packages=find_packages(),
    install_requires=[
        'django>=1.4',
    ],
    tests_require=[
        'mock',
        'pytest',
        'pytest-django',
    ]
)
