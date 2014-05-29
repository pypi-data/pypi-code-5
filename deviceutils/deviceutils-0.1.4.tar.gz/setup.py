#!/usr/bin/env python
"""
"""
import sys
__python_version__ = dict()
try:
    __python_version__['major'] = sys.version_info.major
except AttributeError:
    __python_version__['major'] = sys.version_info[0]
try:
    __python_version__['minor'] = sys.version_info.minor
except AttributeError:
    __python_version__['minor'] = sys.version_info[1]

from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

REQ_PKGS_ALL = ['future', 'pyserial']
REQ_PKGS_PY26 = []

required_packages = REQ_PKGS_ALL
if (__python_version__['major'], __python_version__['minor']) in [(2, 6)]:
    required_packages += REQ_PKGS_PY26


setup(name='deviceutils',
      version='0.1.4',
      description='Python Device Interaction Utilities',
      long_description=long_description,
      keywords='control communication device instrumentation lab laboratory manufacturing science',
      author='Sean Anthony Finucane',
      author_email='s.finucane001@gmail.com',
      url='https://github.com/sfinucane/deviceutils',
      license='Apache License, Version 2.0',
      classifiers=[
           'Development Status :: 2 - Pre-Alpha',
           'Intended Audience :: Developers',
           'Intended Audience :: Science/Research',
           'Intended Audience :: Education',
           'Intended Audience :: Manufacturing',
           'License :: OSI Approved :: Apache Software License',
           'Operating System :: MacOS :: MacOS X',
           'Operating System :: Microsoft :: Windows',
           'Operating System :: POSIX',
           'Programming Language :: Python',
           'Programming Language :: Python :: 2.6',
           'Programming Language :: Python :: 2.7',
           'Programming Language :: Python :: 3',
           'Topic :: Scientific/Engineering',
           'Topic :: Software Development :: Libraries',
           'Topic :: Utilities'
      ],
      install_requires=required_packages,
      zip_safe=True,
      platforms='any',
      provides=['deviceutils'],
      data_files=[('', ['README.md', 'LICENSE', 'NOTICE'])],
      packages=['deviceutils',
                'deviceutils.error',
                'deviceutils.io',
                'deviceutils.device',
                'deviceutils.action',
                'deviceutils.ieee488'],
      )
