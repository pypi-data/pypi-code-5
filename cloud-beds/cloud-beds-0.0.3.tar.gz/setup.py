#!/usr/bin/env python3
from distutils.core import setup

setup(name='cloud-beds',
    author='Thomas Levine',
    author_email='_@thomaslevine.com',
    description='Find beds in the cloud.',
    url='https://github.com/tlevine/cloud-beds.git',
    classifiers=[
        'Intended Audience :: Developers',
    ],
    packages=['cloud_beds'],
    scripts=['bin/cloud-beds'],
    install_requires = ['requests','craigsgenerator'],
    tests_require = ['nose'],
    version='0.0.3',
    license='AGPL'
)
