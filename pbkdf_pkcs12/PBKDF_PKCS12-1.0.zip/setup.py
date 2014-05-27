#!/usr/bin/env python

# Use setuptools, if available.  Otherwise, fall back to distutils.
try:
    from setuptools import setup
except ImportError:
    import sys
    sys.stderr.write("warning: Proceeding without setuptools\n")
    from distutils.core import setup

setup(
    name='PBKDF_PKCS12',
    py_modules=['PBKDF_PKCS12'],
    version='1.0',
    test_suite='test',
    description='PKCS#12 v1.0 PBKDF Module',
    author='koha',
    author_email='kkoha@msn.com',
    url='http://kkoha.tistory.com/entry/Python-PKCS12-v10-PBKDF-Module',
    keywords = "PBKDF1,PBKDF2,key derivation,password key derivation,PBKDF,PKCS12,PKCS#12,PKCS,crypto",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security :: Cryptography',
    ],
    long_description="""\
This module implements the password-based key derivation function, specified in RSA PKCS#12.
""")
