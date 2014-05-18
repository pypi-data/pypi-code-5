from distutils.core import setup

from commasearch import __version__

setup(name='commasearch',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Search for data tables.',
      url='https://github.com/tlevine/commasearch',
      packages=['commasearch'],
      install_requires = [
          'special_snowflake >= 0.0.8',
          'pickle_warehouse >= 0.0.18',
          'requests>=2.2.1',
      ],
      tests_require = ['nose'],
      version=__version__,
      license='AGPL',
      classifiers=[
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
)
