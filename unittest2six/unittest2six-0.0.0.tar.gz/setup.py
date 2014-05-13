import os
import sys
from setuptools import setup

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    install_requires = ['unittest2']
elif PY3:
    install_requires = ['unittest2py3k']

this_dir = os.path.dirname(__file__)
long_description = "\n" + open(os.path.join(this_dir, 'README.rst')).read()

setup(
    name='unittest2six',
    version='0.0.0',
    description=('Meta-package for unittest2 functionality on both Python 2 and Python 3'),
    long_description=long_description,
    keywords='testing unittest2',
    author='Marc Abramowitz',
    author_email='marc@marc-abramowitz.com',
    url='https://github.com/msabramo/unittest2six',
    zip_safe=False,
    install_requires=install_requires,
    test_suite='panci.tests',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
)
