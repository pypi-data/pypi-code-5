# coding=utf-8

from setuptools import setup


setup(
    name='django-fs-email-helper',
    version = '0.1',
    packages = ['email_helper'],
    include_package_data = True,
    author = 'Yuri Lya',
    author_email = 'yuri.lya@fogstream.ru',
    url = 'https://bitbucket.org/fogstream/django-fs-email-helper',
    license = 'The MIT License (MIT)',
    description = 'The Django-related reusable app provides the ability to send multipart emails and store them in a database.',
    long_description = open('README.txt').read(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
