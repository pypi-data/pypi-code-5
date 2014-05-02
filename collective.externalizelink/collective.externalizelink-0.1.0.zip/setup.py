from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.externalizelink',
      version=version,
      description="Controls when Plone must open links in external page (in an accessible way)",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone link popup open',
      author='keul',
      author_email='luca@keul.it',
      url='https://github.com/keul/collective.externalizelink',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.registry',
          'collective.jsconfiguration',
          'collective.regjsonify',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
