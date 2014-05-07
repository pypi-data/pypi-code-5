from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="crypt_me",
      version="0.140",
      description="Caesar cipher with qt GUI",
      py_modules=['crypt_me','ez_setup'],
      long_description="""\
      Caesar cipher with qt GUI
""",
      author="Martin Bednar",
      author_email="martin.bednar@hotmail.sk",
      license="GNU GPL v3 license",
      keywords="Caesar",
      #packages=find_packages(exclude='tests'),
      #package_data={'mypackage': ['data/*.xml']},
      )