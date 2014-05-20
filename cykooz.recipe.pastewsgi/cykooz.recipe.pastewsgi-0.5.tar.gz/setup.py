# cykooz.recipe.pastewsgi
# Copyright (C) 2014 Cykooz
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from setuptools import setup, find_packages

install_requires = [
    'setuptools',
    'zc.buildout',
    'zc.recipe.egg',
]

tests_require = []

extras_require = dict(
    test=tests_require,
)

setup(
    name='cykooz.recipe.pastewsgi',
    version='0.5',
    url='https://bitbucket.org/cykooz/cykooz.recipe.pastewsgi',
    license='GPL 2',
    author='Cykooz',
    author_email='saikuz@mail.ru',
    description="Buildout recipe to create paste.deploy entry points for mod_wsgi or uwsgi",
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    classifiers=[
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cykooz', 'cykooz.recipe'],
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=install_requires + tests_require,
    test_suite="cykooz.recipe.pastewsgi.tests",
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [zc.buildout]
    default = cykooz.recipe.pastewsgi:Recipe
    """
)
