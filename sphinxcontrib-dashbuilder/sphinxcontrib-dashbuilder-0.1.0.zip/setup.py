# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst', 'rt') as f:
    long_desc = f.read()

requires = [
    'Sphinx>=1.2',
    'six',
]

extras_require = {
    'test': [
        'nose2',
    ]
}

setup(
    name='sphinxcontrib-dashbuilder',
    version='0.1.0',
    #url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    url='http://bitbucket.org/shimizukawa/sphinxcontrib_dashbuilder',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-dashbuilder',
    license='BSD',
    author='shimizukawa',
    author_email='shimizukawa@gmail.com',
    description="Sphinx builder extension to generate a 'Documentation Set' for `dash API browser`.",
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    extras_require=extras_require,
    namespace_packages=['sphinxcontrib'],
)
