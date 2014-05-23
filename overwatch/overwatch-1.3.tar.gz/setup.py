#!/usr/bin/env python2

'''Overwatch: Python Logging Browser.

This package includes special logger and GUI written in GTK2
that allows you to perform real-time logs monitoring from a
bunch of applications.
'''

from distutils.core import setup
from setuptools import find_packages

classifiers = '''
Development Status :: 4 - Beta
Environment :: Console
Environment :: X11 Applications :: GTK
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Intended Audience :: System Administrators
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Topic :: Software Development :: Debuggers
Topic :: System :: Monitoring
'''

doclines = __doc__.split('\n')

setup(name='overwatch',
        version='1.3',
        author='Andrew Dunai',
        author_email='andunai@gmail.com',
        url='http://andrewdunai.com/projects/overwatch/',
        packages=find_packages(),
        package_data={'overwatch': ['data/*']},
        platforms=['unix'],
        classifiers=filter(None, classifiers.split("\n")),
        description=doclines[0],
        long_description='\n'.join(doclines[2:]),
     )
