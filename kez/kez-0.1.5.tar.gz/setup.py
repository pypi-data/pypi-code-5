# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

__version__ = "0.1.5"

setup(
    name="kez",
    version=__version__,
    description="CLI for tracking and building documents, specifically Pelican static blogs",
    author="gmf",
    author_email = "gmflanagan@outlook.com",
    classifiers=["Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Programming Language :: Python",
                "Topic :: Software Development :: Libraries",
                "Topic :: Software Development :: Libraries :: Python Modules",
                ],
    url="https://github.com/averagehuman/kez",
    license="BSD",
    packages = find_packages(),
    scripts = [
        'bin/kez',
    ],
    include_package_data=True,
    zip_safe=False,
    tests_require=['pytest'],
)
    
