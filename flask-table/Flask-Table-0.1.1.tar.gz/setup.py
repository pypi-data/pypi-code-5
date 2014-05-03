from distutils.core import setup

setup(
    name='Flask-Table',
    packages=['flask_table'],
    install_requires=['Flask', 'Babel'],
    version='0.1.1',
    author='Andrew Plummer',
    author_email='plummer574@gmail.com',
    url='https://github.com/plumdog/flask_table',
    description='HTML tables for use with the Flask micro-framework',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Framework :: Flask',
    ])
