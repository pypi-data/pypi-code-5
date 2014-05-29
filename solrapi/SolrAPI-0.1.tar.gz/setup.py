#!/usr/bin/env python
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

tests_require = []
PY2 = sys.version_info[0] == 2

if PY2:
    tests_require.append('mock')

setup(
    name="SolrAPI",
    version='0.1',
    description="Python implementation of the main operation in the Solr API Rest",
    author="Jamil Atta Junior",
    author_email="atta.jamil@gmail.com",
    license="BSD",
    url="https://github.com/picleslivre/solrapi",
    py_modules=['SolrAPI'],
    keywords='solr api lucene rest',
    maintainer_email='atta.jamil@gmail.com',
    download_url='',
    classifiers=[
        "Topic :: System",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Customer Service",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: Portuguese (Brazilian)",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    setup_requires=["requests", "lxml"],
    tests_require=tests_require,
    test_suite='tests'
)
