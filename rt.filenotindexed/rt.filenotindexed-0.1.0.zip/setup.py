from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='rt.filenotindexed',
      version=version,
      description="Force Plone to not index your files in SearchableText",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        ],
      keywords='plone index catalog search file',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://github.com/RedTurtle/rt.filenotindexed',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rt'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          #'Products.ATContentTypes',
          #'plone.app.blob',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
