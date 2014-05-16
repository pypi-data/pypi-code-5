from setuptools import setup, find_packages
import os

version = '1.5.2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'bootstrap_select', 'test_bootstrap_select.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.bootstrap_select',
    version=version,
    description="Fanstatic packaging of bootstrap-select.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://github.com/tmassman/js.bootstrap_select',
    download_url='http://pypi.python.org/pypi/js.bootstrap_select',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.bootstrap',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'bootstrap_select = js.bootstrap_select:library',
        ],
    },
)
