"""
JiveData
--------

To Install
``````````

.. code:: bash

    $ pip install JiveData

To run the webapp
`````````````````

.. code:: bash

    $ python run_webapp.py

To run the alerts
`````````````````

.. code:: bash

    $ python run_alerts.py


Links
`````

* `API Documentation <https://api.jivedata.com/documentation/>`_
* `Github Repo <https://github.com/jivedata/jivedata>`_

"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

version = '0.1'

setup(
    name='JiveData',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    version=version,
    description='The code that powers www.jivedata.com, our email alerts, '
                'and twitter notifications',
    long_description=__doc__,
    license='BSD',
    author='Jive Data',
    author_email='support@jivedata.com',
    install_requires=[
        'Flask',
        'Jinja2',
        'requests',
    ],
    url='https://www.jivedata.com',
    download_url='https://github.com/jivedata/jivedata/tarball/' + version,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
    ],
)
