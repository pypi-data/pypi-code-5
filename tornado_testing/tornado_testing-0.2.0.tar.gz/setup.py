
import os
from setuptools import setup

if os.path.isfile('tornado_testing/layer.rst'):
    long_desc = open('tornado_testing/layer.rst').read()
else:
    long_desc = ''


setup(
    name='tornado_testing',
    version='0.2.0',
    author='Mathias Fußenegger',
    author_email='pip@zignar.net',
    description='tornado testlayer for use with zope.testrunner',
    long_description=long_desc,
    url='https://github.com/mfussenegger/tornado-testing',
    platforms=['any'],
    packages=['tornado_testing'],
    extras_require={
        'test': ['tornado']
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
