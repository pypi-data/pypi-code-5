import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_broker',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A simple app to facilitate currency conversions.',
    long_description=README,
    url='http://github.com/parsenz/django-broker',
    author='Seiyifa Tawari',
    author_email='seiyifa.tawari@gmail.com',
    install_requires=['Django'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
