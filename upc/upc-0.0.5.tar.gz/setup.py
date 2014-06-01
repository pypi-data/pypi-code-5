# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='upc',
    version=__import__('upc').__version__,
    url='http://github.com/likang/upc',
    download_url='http://pypi.python.org/pypi/upc',
    description='A simple command-line tool for managing upyun files.',
    long_description='A simple command-line tool for managing upyun files.',
    license='MIT',
    platforms=['any'],
    py_modules=['upc'],
    author='Kang Li',
    author_email='i@likang.me',
    keywords=['upyun', 'console', 'commandline', 'command'],
    install_requires=[
        'upyun >= 2.2.0',
    ],
    entry_points={
        'console_scripts': [
            'upc=upc:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
