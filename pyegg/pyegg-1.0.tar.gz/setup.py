#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pyegg',
    version='1.0',
    description='Python Eggs',
    author='Daniel Pimentel',
    author_email='d4n1h4ck@gmail.com',
    url='http://about.me/d4n1',
    packages=['pyegg'],
        long_description="""\
        PyEgg is a example for python egg...
        """,
        classifiers=[
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Topic :: Internet",
        ],
        keywords='package egg',
        license='GPL',
        install_requires=[
            'setuptools',
            'greenlet',
        ],
        )
