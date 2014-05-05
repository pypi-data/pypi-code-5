# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="tzgeo",
    version="0.0.1",
    description="Get the timezone for a location",
    long_description=open('README.md').read(),
    author='Mark Smith',
    author_email='mark.smith@practicalpoetry.co.uk',
    url='https://github.com/bedmondmark/tzgeo',
    license='MIT License',

    packages=['tzgeo'],
    include_package_data=True,
    package_data={'tzgeo': ['tzgeo.sqlite']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'pyspatialite>=3.0.1-alpha-0',
    ],
    zip_safe=False,
)
