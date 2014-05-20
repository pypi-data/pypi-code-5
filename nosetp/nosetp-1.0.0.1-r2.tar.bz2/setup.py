import ez_setup
ez_setup.use_setuptools()


from setuptools import setup, find_packages
import sys

sys.path.insert(0, 'nosetp')
import version as proj_version

import nosetp.version as proj_version


setup(
    name='nosetp',
    version=proj_version.setuptools_string(),
    #description='Brief description of the package.',
    author='Brian Mearns',
    author_email='bmearns@ieee.org',
    url='https://bitbucket.org/bmearns/nosetp',
    license='LICENSE.txt',

    include_package_data = True,    #Uses MANIFEST.in
    
    packages = find_packages('.', exclude=["tests"]),   #Search for modules, identified by __init__.py

    requires = ['nose (>=0.9.2)', 'docit',],

    #For nosetests command, and sphinx commands (build_sphinx and upload_sphinx)
    setup_requires = ['nose>=1.0', 'sphinx>=0.5', 'sphinx_rtd_theme', 'docit'],

    #Less desirable than the nosetests command, but allows you to use the
    # standard `tests` command to run nosetests.
    test_suite = 'nose.collector',
    tests_require = ['nose>=1.0', 'pychangelog'],

    entry_points = {
        'distutils.commands': [
            'nosetp = nosetp.commands:nosetp',
        ],
    },

    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
)

