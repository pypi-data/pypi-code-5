#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join, dirname
from setuptools import setup, find_packages


def get_version(fname='djinter/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])

setup(
    name='django-code-linter',
    version=get_version(),
    packages=find_packages(),
    requires=['python (>= 2.7)', ],
    install_requires=[],
    tests_require=[],
    description='suite to test django code style',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author='42 Coffee Cups',
    author_email='contact@42cc.co',
    url='https://github.com/42cc/django-code-linter',
    download_url='https://github.com/42cc/django-code-linter/archive/master.zip',
    license='BSD License',
    keywords=['ripple', 'api'],
    entry_points={
        'console_scripts': ['djinter = djinter.main:main'],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
