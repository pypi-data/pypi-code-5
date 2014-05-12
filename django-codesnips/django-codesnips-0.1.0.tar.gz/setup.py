#! /usr/bin/env python

"""
Distutils setup file for codesnips
"""

from setuptools import setup, find_packages
from codesnips import __version__

setup(
    name='django-codesnips',
    version=__version__,
    packages=find_packages(),

    # Metadata
    author='',
    author_email='opensource(at)packetperception.org',
    description='Django code snippets',
    long_description="""
    Snippets of code that are useful with Django.
    """,
    license='MIT',
    url='https://github.com/PacketPerception/django-codesnips',
    keywords='Django',
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    install_requires=[
            'django>=1.6',
    ],
)
