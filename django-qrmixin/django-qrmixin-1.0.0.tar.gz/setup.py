#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-qrmixin',
    version='1.0.0',
    description="Provides a QR code generating mixin for django models",
    author="Danemco, LLC",
    author_email='dev@velocitywebworks.com',
    url='https://bitbucket.org/freakypie/django-qrmixin',
    packages=find_packages(),
    install_requires=['qrcode'],
)
