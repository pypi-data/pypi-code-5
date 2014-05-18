import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_version():
    """Extract and return version number from the packages '__init__.py'."""
    init_path = os.path.join('pypiuploader', '__init__.py')
    content = read_file(init_path)
    match = re.search(r"__version__ = '([^']+)'", content, re.M)
    version = match.group(1)
    return version


def read_file(filename):
    """Open and a file, read it and return its contents."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as f:
        return f.read()


class PyTest(TestCommand):

    """Command to run unit tests after in-place build."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'tests',
            'pypiuploader',
            '--pep8',
            '--flakes',
            '--cov', 'pypiuploader',
            '--cov-report', 'term-missing',
        ]
        self.test_suite = True

    def run_tests(self):
        # Importing here, `cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


install_requires = [
    'requests',
]
tests_require = [
    'mock',
    'pytest',
    'pytest-cov',
    'pytest-flakes',
    'pytest-pep8',
]

setup(
    name='pypi-uploader',
    version=get_version(),
    author='Ignacy Sokolowski',
    author_email='ignacy.sokolowski@gmail.com',
    description='Upload source distributions to your PyPI server.',
    long_description=read_file('README.rst'),
    url='https://github.com/ignacysokolowski/pypi-uploader',
    install_requires=install_requires,
    tests_require=tests_require,
    license=read_file('LICENSE'),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=['pypiuploader'],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'pypiupload = pypiuploader.commands:main',
        ],
    }
)
