# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='ups',
    version='0.0.1',
    url='http://github.com/likang/ups',
    download_url='http://pypi.python.org/pypi/ups',
    description='A simple upyun server',
    long_description='A simple upyun server',
    license='MIT',
    platforms=['any'],
    py_modules=['ups'],
    author='Kang Li',
    author_email='i@likang.me',
    keywords=['upyun', 'server'],
    entry_points={
        'console_scripts': [
            'ups=ups:main',
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

