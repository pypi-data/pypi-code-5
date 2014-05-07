#!/usr/bin/python

""" setup.py for mps.

https://np1.github.com/mps

"""

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

readme = open("README.rst").read()
license = open("LICENSE").read()

setup(
    name="mps",
    version="0.20.10",
    description="Search, Stream and Download MP3",
    keywords=["MP3", "music", "audio", "search", "stream", "download"],
    author="nagev",
    license=license,
    long_description=readme,
    author_email="np1nagev@gmail.com",
    url="http://github.com/np1/mps/",
    download_url="https://github.com/np1/mps/tarball/master",
    scripts=['mps'],
    package_data={"": ["LICENSE", "README.rst"]},
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Internet :: WWW/HTTP"],
)
