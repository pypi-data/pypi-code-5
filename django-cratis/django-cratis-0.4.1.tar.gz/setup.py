import os
from setuptools import setup, find_packages
# from tests import PyTest

setup(
    name='django-cratis',
    version='0.4.1',
    packages=find_packages(),

    url='',
    license='MIT',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Django-cratis is a way to group together django applications, so they form reusable features.',
    long_description='',
    install_requires=[
        'django>=1.4',
        'django-configurations',
        'setuptools',
        'inject'
    ],

    entry_points={
        'console_scripts': [
            'cratis = cratis.cli:cratis_cmd',
            'cratis-init = cratis.cli:cratis_init_cmd',
        ],
    },
)

