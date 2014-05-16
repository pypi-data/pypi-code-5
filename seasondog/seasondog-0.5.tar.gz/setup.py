#!/usr/bin/env python

from distutils.core import setup

setup(name='seasondog',
      version='0.5',
      description='Tool for tracking you progress in watching series and playing you the next episode',
      author='Vasiliy Horbachenko',
      author_email='shadow.prince@ya.ru',
      url='http://github.com/shadowprince/seasondog',
      scripts=['seasondog/sdog'],
      packages=['seasondog', ],
     )
