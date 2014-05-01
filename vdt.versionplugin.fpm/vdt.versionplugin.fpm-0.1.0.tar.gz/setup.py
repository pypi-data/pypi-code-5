from setuptools import find_packages, setup

pkgname = "vdt.versionplugin.fpm"

setup(name=pkgname,
      version="0.1.0",
      description="Version Increment Plugin that builds with fpm",
      author="Martijn Jacobs",
      author_email="martijn@kamaramusic.nl",
      maintainer="Martijn Jacobs",
      maintainer_email="martijn@kamaramusic.nl",
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



