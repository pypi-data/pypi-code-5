from setuptools import setup, find_packages

requirements = open('requirements.txt').readlines()

setup(
    name = "sample_helloworld_egg",
    version = "0.1",
    packages = find_packages(),
    install_requires = requirements,
    entry_points = {
        'console_scripts': [
            'helloserver = helloworld.web:main',
        ],
    },
)
