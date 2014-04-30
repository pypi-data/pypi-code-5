from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "rw",
    version = "0.0.2",
    packages = find_packages(),
    scripts = ['scripts/rw'],

    install_requires = ['docopt', 'six'],
    
    author = "Ben Pringle",
    author_email = "ben.pringle@gmail.com",
    url = "http://github.com/Pringley/rw",
    description = "Generate random words (e.g. for passwords)",
    license = "MIT",
)
