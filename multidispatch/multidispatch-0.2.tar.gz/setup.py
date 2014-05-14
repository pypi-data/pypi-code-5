# -*- coding: utf8 -*-
from distutils.core import setup
import os

setup(name='multidispatch',
      version='0.2',
      description='Create multi-dispatch functions.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-multimethod',
      long_description=(
'''Multidispatch functions: easily define multiple implementations for the same 
function depending on the number and type of its arguments.
'''),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          ],
      package_dir={'': 'src'},
      py_modules=['multidispatch'],
      requires=[],
)
