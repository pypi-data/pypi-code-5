from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="crypt_me",
      version="0.02",
      description="Caesar cipher with gui",
      py_modules=['crypt_me','ez_setup'],
      long_description="""\
      Caesar cipher with gui
""",
      author="Martin Bednar",
      author_email="martin.bednar@hotmail.sk",
      #packages=find_packages(exclude='tests'),
      #package_data={'mypackage': ['data/*.xml']},
      )