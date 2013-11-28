#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

import os

def get_long_description():
    path = os.path.join(os.path.dirname(__file__), 'README.rst')
    with open(path) as f:
        return f.read()

setup(
    name='django-iban',
    version='0.2.3',
    license='BSD',
    description='A validated IBAN field for Django models',
    long_description=get_long_description(),
    url='https://github.com/benkonrath/django-iban',

    author=u'Ben Konrath',
    author_email='ben@bagu.org',

    packages=find_packages(),
    package_data={'django_iban': ['locale/*/LC_MESSAGES/*.po',
                                  'locale/*/LC_MESSAGES/*.mo']},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.4',
        'django-countries==1.5',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
