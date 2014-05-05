import sys
from setuptools import setup, find_packages

setup(
    name='pulley',
    version='0.0.1',
    author='Jimmie Goode',
    author_email='jimmie@quantcluster.com',
    url='https://github.com/quantcluster/pulley.git',
    description='Live trading with zipline and swigibpy via Interactive Brokers.',
    long_description='',
    packages=find_packages(),
    license='',
    classifiers=[
    ],
    install_requires=[
        #'zipline', # requires a custom zipline that should be installed first
        'swigibpy',
        'psycopg2',
        'tzlocal',
        'django',
        'celery',
        'django-celery',
    ],
)
