"""
Script to generate the installer for coopr.neos
"""

from setuptools import setup, find_packages

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: End Users/Desktop
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: Microsoft :: Windows
Operating System :: Unix
Programming Language :: Python
Topic :: Scientific/Engineering :: Mathematics
Topic :: Software Development :: Libraries :: Python Modules
"""

setup(name = "coopr.neos",
      version = "1.1.1",
      maintainer='William E. Hart',
      maintainer_email='wehart@sandia.gov',
      url = 'https://software.sandia.gov/svn/public/coopr/coopr.neos',
      license = 'BSD',
      platforms = ["any"],
      description = 'Coopr utilities',
      classifiers = filter(None, classifiers.split("\n")),
      packages = ['coopr', 'coopr.neos'],
      keywords = ['optimization'],
      namespace_packages=['coopr']
      )
