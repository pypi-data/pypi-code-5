from setuptools import setup
import vlcli

config = {
    'name': 'vlcli',
    'description': 'Command Line Interface to VeraxLabs REST API',
    'long_description': open('README.rst').read(),
    'author': 'Prashant Singhal',
    'url': 'http://www.veraxlabs.com',
    'author_email': 'psl@veraxlabs.com',
    'version': vlcli.__version__,
    'install_requires': [],
    'packages': ['vlcli'],
    'scripts': ['bin/vl'],
    'keywords': 'cloud devops sysadmin administration setup monitoring security',
    'license': 'Apache License 2.0',
    'classifiers': (
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Operating System',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ),
}

setup(**config)
