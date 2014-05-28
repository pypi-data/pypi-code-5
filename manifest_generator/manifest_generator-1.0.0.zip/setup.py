import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
# from https://pythonhosted.org/an_example_pypi_project/setuptools.html
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "manifest_generator",
    version = "1.0.0",
    author = "Kevin Dahlhausen",
    author_email = "kpd@powertwenty.com",
    description = ("A utility to smartly generate an HTML5 application cache manifest"),
    license = "GPL3",
    keywords = "html5 cache manifest",
    url = "https://github.com/kdahlhaus/manifest_generator",
    packages=['manifestgen',],
    long_description="This package contains a utility to generate the HTML5 application cache manifest file.   Running it multiple times only changes the manifest if the manifest contents or contents of files listed in the cache change. ",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console",
    ],
    install_requires=["glob2",],
    scripts=['bin/manifest_gen'],
)

