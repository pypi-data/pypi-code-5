#!/usr/bin/env python
"""
"""
from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='deviceutils',
      version='0.1.2',
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
           'Programming Language :: Python :: 3.2',
           'Programming Language :: Python :: 3.3',
           'Programming Language :: Python :: 3.4',
           'Topic :: Scientific/Engineering',
           'Topic :: Software Development :: Libraries',
           'Topic :: Utilities'
      ],
      install_requires=['pyserial'],
      zip_safe=True,
      platforms='any',
      provides=['deviceutils'],
      data_files=[('', ['README.md', 'LICENSE', 'NOTICE'])],
      packages=['deviceutils',
                'deviceutils.io',
                'deviceutils.device',
                'deviceutils.action',
                'deviceutils.ieee488'],
      )
