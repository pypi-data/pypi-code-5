import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = 'test'
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='fowler.switchboard',
    version='0.1',
    description='A wrapper around Christopher Potts\' swda.py',
    long_description='''''',
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    author='Dmitrijs Milajevs, Christopher Potts',
    author_email='dimazest@gmail.com',
    url='http://www.eecs.qmul.ac.uk/~dm303/',
    license='Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['fowler'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'cython>=0.13',
        'nltk',
        'opster',
        'pandas',
        'python-dateutil',
        'pyyaml',
        'scikit-learn',
        'scipy',
        'setuptools',
        'tables',
    ],
    entry_points={
        'console_scripts': [
            'sw = fowler.switchboard.main:dispatch',
        ],
    },
    tests_require=['pytest>=2.4.2'],
    cmdclass={'test': PyTest},
)
