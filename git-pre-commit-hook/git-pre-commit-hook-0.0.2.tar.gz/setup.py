import codecs
import os
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(HERE, *parts), 'r').read()


setup(
    name='git-pre-commit-hook',
    description='pre-commit hook for Git',
    long_description=read('README.rst'),
    version='0.0.2',
    license='MIT',
    author='Evgeny Vereshchagin',
    author_email='evvers@ya.ru',
    url='https://github.com/evvers/git-pre-commit-hook',
    packages=find_packages(),
    install_requires=[
        'git-pre-commit-hook-utils',
        'flake8',
        'restructuredtext_lint',
    ],
    entry_points={
        'console_scripts': [
            'git-pre-commit-hook=git_pre_commit_hook:main',
        ],
        'git_pre_commit_hook.extensions': [
            'file_size=git_pre_commit_hook.builtin_plugins.file_size_check',
            'json=git_pre_commit_hook.builtin_plugins.json_check',
            'flake8=git_pre_commit_hook.builtin_plugins.flake8_check',
            'rst=git_pre_commit_hook.builtin_plugins.rst_check',
        ],
    }
)
