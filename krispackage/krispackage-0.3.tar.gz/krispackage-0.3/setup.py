import os
from setuptools import setup

README = "this is the long read me that everyone wants"

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='krispackage',
    version='0.3',
    packages=[],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app that does absolutely nothing.',
    long_description=README,
    url = 'https://github.com/axellerate/testing', # use the URL to the github repo
    download_url = 'https://github.com/axellerate/testing/tarball/0.1', # I'll explain this in a second
    author='Kris Vukasinovic',
    author_email='axellerate@example.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)