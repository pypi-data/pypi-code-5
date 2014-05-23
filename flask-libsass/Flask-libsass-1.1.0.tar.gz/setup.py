"""
Flask-libass
------------

Flask extension for serving css generated from sass or scss.
Uses the bindings to libsass at https://pypi.python.org/pypi/sass/
"""
from setuptools import setup


setup(
    name='Flask-libsass',
    version='1.1.0',
    url='https://github.com/bwhmather/flask-libsass/',
    license='BSD',
    author='Ben Mather',
    author_email='bwhmather@bwhmather.com',
    description='Flask extension for building css from sass or scss',
    long_description=__doc__,
    py_modules=['flask_libsass'],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask >= 0.9',
        'sass',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Compilers',
    ]
)
