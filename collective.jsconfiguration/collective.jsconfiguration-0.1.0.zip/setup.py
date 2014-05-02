from setuptools import setup, find_packages
import os

version = '0.1.0'

tests_require = ['plone.app.testing', ]

setup(name='collective.jsconfiguration',
      version=version,
      description="General approach for adding JavaScript configuration (and i18n data) to Plone products",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        ],
      keywords='plone javascript configuration i18n',
      author='keul',
      author_email='luca@keul.it',
      url='https://github.com/keul/collective.jsconfiguration',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
