'''setup for package'''
from setuptools import setup

with open('README.rst') as h_readme:
    LONG_DESCRIPTION = h_readme.read()

DESCRIPTION = "A collection of handy modules, almost guaranteed to get you "\
              "into trouble."
setup(name='dhp',
      version='0.0.2',
      packages=['dhp', 'dhp.test', 'dhp.xml'],
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author="Jeff Hinrichs",
      author_email="jeffh@dundeemt.com",
      url="https://bitbucket.org/dundeemt/dhp",   # project home page, if any
      package_data={
          # If any package contains *.txt or *.rst files, include them:
          '': ['README.rst', 'LICENSE.txt', '*.rst'],
      },
      license='BSD',
      keywords="phrasebook hungarian",
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],
)
