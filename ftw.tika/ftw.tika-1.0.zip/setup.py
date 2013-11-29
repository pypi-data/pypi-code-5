from setuptools import setup, find_packages
import os

version = '1.0'

tests_require = [
    'unittest2',
    'ftw.testing',
    'plone.testing',
    'plone.app.testing',
    'Products.CMFCore',
    'zope.configuration',
    ]

setup(name='ftw.tika',
      version=version,
      description='Apache Tika integration for Plone using portal transforms.',
      long_description=open('README.rst').read() + '\n' +
      open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development',
        ],

      keywords='plone ftw tika full text indexing apache',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.tika',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',

        # Zope
        'zope.component',
        'zope.interface',
        'zope.schema',
        'ZODB3',

        # Plone
        'Products.GenericSetup',
        'Products.PortalTransforms',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points='''
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
