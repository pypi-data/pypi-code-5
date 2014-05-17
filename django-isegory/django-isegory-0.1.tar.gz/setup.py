import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-isegory',
    version='0.1',
    packages=['isegory'],
    include_package_data=True,
    license='AGPL',
    description='A simple Django app to declare the provenance of a dataset.',
    long_description=README,
    url='http://github.com/jdelacueva/django-isegory/',
    author='Javier de la Cueva',
    author_email='jdelacueva@derecho-internet.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
