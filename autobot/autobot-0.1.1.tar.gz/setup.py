import os
import sys
from setuptools import setup

short_description = "buildbot front-end incarnation"
try:
    description = file('README.txt').read()
except IOError:
    description = short_description

version = '0.1.1'

setup(name='autobot',
      version=version,
      description=short_description,
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='buildbot automation',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/autobot',
      license='MPL',
      packages=['autobot'],
      include_package_data=True,
      package_data={'': ['template/master/*',
                         'template/slave/*',
                         'template/*.*']},
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'buildbot>=0.8.5',
          'buildbot-slave>=0.8.5',
          'virtualenv',
          'MakeItSo',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      create-autobot = autobot.template:create_autobot
      create-autobot-master = autobot.template:create_master
      create-autobot-slave = autobot.template:create_slave
      create-autobot-project = autobot.template:create_project
      parse-autobot-config = autobot.config:main
      """,
      )
