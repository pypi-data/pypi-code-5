#!/usr/bin/env python

from distutils.core import setup

setup(name='mysql2csv',
      version='0.2',
      description='Convert some or all tables in a MySQL database into CSV files.',
      author='Elcio Ferreira',
      author_email='elcio@visie.com.br',
      maintainer='Ricardo Lafuente',
      maintainer_email='r@manufacturaindependente.org',
      url='http://github.com/rlafuente/mysql2csv/',
      download_url='https://github.com/rlafuente/mysql2csv/tarball/master',
      scripts=['mysql2csv'],
      keywords=['mysql', 'csv'],
      license="MIT"
     )

