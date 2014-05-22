# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except:
    from distutils.core import setup


setup(
    name='chartbeatpy',
    version='0.2.1',
    description='A charbeat API wrapper.',
    long_description=open('README.rst').read(),
    author='Timothée Peignier',
    author_email='timothee.peignier@tryphon.org',
    url='https://github.com/detroit-media-partnership/chartbeatpy',
    packages=['chartbeatpy'],
    keywords=['chartbeat', 'API'],
    include_package_data=True,
    license='LICENSE.rst',
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
