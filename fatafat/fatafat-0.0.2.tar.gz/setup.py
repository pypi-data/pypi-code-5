#!/usr/bin/env python

from setuptools import setup


# Convert Markdown to RST because PyPI likes RST! Fallback on Markdown if
# pypandoc is not available.
try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as f:
        readme = f.read()


requires = ['markdown >= 2.4', 'jinja2 >= 2.7', 'sh >= 1.09', 'six']

entry_points = {
    'console_scripts': [
        'fatafat = fatafat:main'
    ]
}

setup(
    name='fatafat',
    version='0.0.2',
    url='http://github.com/isubuz/fatafat',
    author='Subhajit Ghosh',
    author_email='i.subhajit.ghosh@gmail.com',
    description='A static blog generator and an offline blogging tool.',
    long_description=readme,
    packages=['fatafat'],
    include_package_data=True,
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
