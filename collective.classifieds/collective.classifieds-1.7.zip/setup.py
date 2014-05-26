from setuptools import setup, find_packages

version = '1.7'
long_description = (
    open('README.rst').read() + '\n' +
    # open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(name='collective.classifieds',
      version=version,
      description="Add classifieds to your Plone intranet or website.",
      long_description=long_description,
      classifiers=[
          'Framework :: Plone',
          'Framework :: Plone :: 4.0',
          'Framework :: Plone :: 4.1',
          'Framework :: Plone :: 4.2',
          'Framework :: Plone :: 4.3',
          # 'Framework :: Plone :: 5.0',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='classifieds sales intranet',
      author='Four Digits (ralph@fourdigits.nl)',
      author_email='ralph@fourdigits.nl',
      url='http://www.plone.org/products/classifieds',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'AccessControl',
          'Acquisition',
          'Products.Archetypes',
          'Products.ATContentTypes',
          'Products.CMFCore',
          'Products.CMFPlone',
          'Products.GenericSetup',
          'Products.validation',
          'setuptools',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
      ],
      extras_require={
          'test': [
              'Products.PloneTestCase',
              'zope.testing',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
