#!/usr/bin/env python

from setuptools import setup, find_packages
from molp import VERSION

url="https://github.com/jeffkit/molp"

long_description="online parameters for app mobile"

setup(name="molp",
      version=VERSION,
      description=long_description,
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url = url,
      long_description=long_description,
      packages=find_packages('.'),
     )


