# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'CHANGELOG.rst')).read()

version = '1.0.0'

install_requires = [
    'drest==0.9.12',
]

setup(name='cuckooapi',
    version=version,
    description="Cuckoo REST API client for Python.",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.4',
      'Topic :: Security',
    ],
    keywords='cuckoo api drest',
    author=u'Roberto Abdelkader Martínez Pérez',
    author_email='robertomartinezp@gmail.com',
    url='https://github.com/nilp0inter/cuckooapi',
    license='LGPLv3',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
