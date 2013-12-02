"""
    Flask-Restless
    ~~~~~~~~~~~~~~

    Flask-Restless is a `Flask <http://flask.pocoo.org>`_ extension which
    facilitates the creation of ReSTful JSON APIs. It is compatible with models
    which have been defined using `SQLAlchemy <http://sqlalchemy.org>`_ or
    `FLask-SQLAlchemy <http://packages.python.org/Flask-SQLAlchemy>`_.

    For more information, check the World Wide Web!

      * `Documentation <http://readthedocs.org/docs/flask-restless>`_
      * `PyPI listing <http://pypi.python.org/pypi/Flask-Restless>`_
      * `Source code repository <http://github.com/jfinkels/flask-restless>`_

"""
import sys
from setuptools import Command
from setuptools import setup

#: The installation requirements for Flask-Restless. Some notes:
#: - ``simplejson`` is only required on Python version 2.5.
#: - ``Flask-SQLAlchemy`` is not required, so the user must install it
#:   explicitly.
#: - Versions less than 2.0 of ``python-dateutil`` support Python 2.5, but
#:   later versions do not.
requirements = ['flask>=0.7', 'sqlalchemy']
if sys.version_info < (2, 6):
    requirements.append('simplejson')
    requirements.append('python-dateutil<2.0')
else:
    requirements.append('python-dateutil!=2.0')


setup(
    author='Jeffrey Finkelstein',
    author_email='jeffrey.finkelstein@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='A Flask extension for easy ReSTful API generation',
    download_url='http://pypi.python.org/pypi/Flask-Restless',
    install_requires=requirements,
    include_package_data=True,
    keywords=['ReST', 'API', 'Flask', 'Elixir'],
    license='GNU AGPLv3+ or BSD',
    long_description=__doc__,
    name='Flask-Restless',
    platforms='any',
    packages=['flask_restless'],
    test_suite='nose.collector',
    tests_require=['nose'],
    url='http://github.com/jfinkels/flask-restless',
    version='0.12.1',
    zip_safe=False
)
