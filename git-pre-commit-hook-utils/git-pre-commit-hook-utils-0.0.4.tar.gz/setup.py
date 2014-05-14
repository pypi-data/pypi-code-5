import codecs
import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(HERE, *parts), 'r').read()


setup(
    name='git-pre-commit-hook-utils',
    version='0.0.4',
    description='utils for implementing git pre-commit hook',
    long_description=read('README.rst'),
    license='MIT',
    author='Evgeny Vereshchagin',
    author_email='evvers@ya.ru',
    url='https://github.com/evvers/git-pre-commit-hook-utils',
    packages=find_packages(),
)
