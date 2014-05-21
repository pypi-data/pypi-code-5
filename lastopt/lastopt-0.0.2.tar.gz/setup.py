import sys
import re

from setuptools import setup
from setuptools import find_packages


module = open('lastopt.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", module))


setup(
    name='lastopt',
    version=metadata['version'],
    author='Andy Gayton',
    author_email='andy@thecablelounge.com',
    py_modules=['lastopt'],
    url='https://github.com/cablehead/lastopt',
    license='MIT',
    description=open('README.md').read().split('\n')[3],
    long_description=open('README.md').read(),
    test_suite='lastopt',
)
