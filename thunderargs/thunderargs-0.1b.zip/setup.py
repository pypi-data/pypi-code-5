from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='thunderargs',
    version='0.1b',
    license='JSON license',
    description='Let you use function annotations (PEP 3107) to get'
                'arguments from flask http requests',
    packages=find_packages(),
    url='https://bitbucket.org/dsupiev/thunderargs',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author="uthunderbird",
    author_email="undead.thunderbird@gmail.com",
)