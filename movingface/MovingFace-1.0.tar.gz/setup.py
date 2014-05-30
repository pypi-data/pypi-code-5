# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='MovingFace',

    version='1.0',

    description="A playing module",
    #long_description=''

    # The project's main homepage.
    url='https://github.com/takoji3/moving_face',

    # Author details
    author='Ryo Kawano',
    author_email='shonancampus@yahoo.co.jp',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    packages=['moving_face'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'moving_face=moving_face.core:start',
        ],
    },
)
