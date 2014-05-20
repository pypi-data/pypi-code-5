from setuptools import setup, find_packages

setup(
    name = "sample_helloworld_egg",
    version = "0.1a",
    packages = find_packages(),
    install_requires = ['flask'],
    entry_points = {
        'console_scripts': [
            'helloserver = helloworld.web:main',
        ],
    },
)
