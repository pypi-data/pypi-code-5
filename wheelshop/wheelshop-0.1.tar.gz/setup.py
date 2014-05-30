# encoding: utf-8
from setuptools import setup, find_packages
from wheelshop import version

setup(
    name = 'wheelshop',
    version = version,
    description = ' your python wheels on a PyPI compatible server using flask and S3',
    author = u'Kristian Øllegaard',
    author_email = 'kristian@livesystems.info',
    zip_safe=False,
    include_package_data = True,
    packages = find_packages(exclude=[]),
    install_requires=[
        'Flask==0.10.1',
        'wheel==0.23.0',
        'boto==2.28.0',
    ],
)