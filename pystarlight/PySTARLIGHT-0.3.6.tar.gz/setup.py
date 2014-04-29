'''
Created on Nov 18, 2012

@author: andre
'''

import os
import sys
import numpy

sys.path.insert(0, os.path.abspath('./src/'))

from distutils.core import setup
from Cython.Build import cythonize

from pystarlight.version import _pystarlight_name_, _pystarlight_version_, _pystarlight_description_, _pystarlight_author_, _pystarlight_author_email_, _pystarlight_license_, _pystarlight_url_, _pystarlight_download_url_, _pystarlight_packages_, _pystarlight_package_dir_, _pystarlight_package_data_, _pystarlight_provides_, _pystarlight_requires_, _pystarlight_classifiers_

setup(name=_pystarlight_name_ ,
      version=_pystarlight_version_,
      description=_pystarlight_description_,
      author=_pystarlight_author_,
      author_email=_pystarlight_author_email_,
      license=_pystarlight_license_,
      url=_pystarlight_url_,
      download_url=_pystarlight_download_url_,
      package_dir=_pystarlight_package_dir_,
      packages=_pystarlight_packages_,
      package_data=_pystarlight_package_data_,
      ext_modules=cythonize(['src/pystarlight/util/*.pyx']),
      include_dirs=[numpy.get_include()],
      provides=_pystarlight_provides_,
      requires=_pystarlight_requires_ ,
      keywords=['Scientific/Engineering'],
      classifiers=_pystarlight_classifiers_,
      )