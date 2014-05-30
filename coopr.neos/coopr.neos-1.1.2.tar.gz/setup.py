"""
Script to generate the installer for coopr.neos
"""

import os

def _find_packages(path):
    """
    Generate a list of nested packages
    """
    pkg_list=[]
    if not os.path.exists(path):
        return []
    if not os.path.exists(path+os.sep+"__init__.py"):
        return []
    else:
        pkg_list.append(path)
    for root, dirs, files in os.walk(path, topdown=True):
      if root in pkg_list and "__init__.py" in files:
         for name in dirs:
           if os.path.exists(root+os.sep+name+os.sep+"__init__.py"):
              pkg_list.append(root+os.sep+name)
    return [pkg for pkg in map(lambda x:x.replace(os.sep,"."), pkg_list)]

from setuptools import setup
packages = _find_packages('coopr')

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
      version = "1.1.2",
      maintainer='William E. Hart',
      maintainer_email='wehart@sandia.gov',
      url = 'https://software.sandia.gov/svn/public/coopr/coopr.neos',
      license = 'BSD',
      platforms = ["any"],
      description = 'Coopr plugins that connect to NEOS solvers',
      classifiers = filter(None, classifiers.split("\n")),
      packages=packages,
      keywords = ['optimization'],
      namespace_packages=['coopr']
      )
