import os
from setuptools import find_packages, setup

pkgname = "vdt.versionplugin.gitchain"

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name=pkgname,
      version="0.0.4",
      description="Instead of building packages as a freezed state, propagate tags between git repositories.",
      long_description=read('README.rst'),
      author="Lars van de Kerkhof",
      author_email="lars@permanentmarkers.nl",
      maintainer="Lars van de Kerkhof",
      maintainer_email="lars@permanentmarkers.nl",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['vdt', 'vdt.versionplugin'],
      zip_safe=True,
      install_requires=[
          "setuptools",
          "vdt.version",
          "vdt.versionplugin.default",
      ],
      entry_points={},
)
