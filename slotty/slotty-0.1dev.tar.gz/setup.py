from setuptools import setup, find_packages
import sys, os, codecs

__version__ = '0.1'
__packagename__ = "slotty"


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


def readlines(fname):
    return read(fname).splitlines()


setup(name=__packagename__,
      version=__version__,
      description="Web Racing Management System",
      long_description=read('README.md'),
      classifiers=["Development Status :: 3 - Alpha",
                   "Environment :: Plugins",
                   "Environment :: Web Environment",
                   "Framework :: Flask",
                   "Intended Audience :: Developers",
                   "Natural Language :: English",
                   "Operating System :: MacOS :: MacOS X",
                   "Operating System :: POSIX :: Linux",
                   "Programming Language :: Python :: 2.7",
                   ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='RMS flask Slotcar slotty',
      author='Rainer Schuster',
      author_email='rainerschuster79@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=readlines('requirements.txt'),
      entry_points={
          #  moved to separate package
          #'slotty.publisher': [
          #     'carrera unit simulator = slotty.datasimulator:poll_sensor',]
      },
      )
