import os
from setuptools import setup

project_dir = os.path.abspath(os.path.dirname(__file__))

long_descriptions = []
for rst in ('README.rst', 'LICENSE.rst'):
    with open(os.path.join(project_dir, rst), 'r') as f:
        long_descriptions.append(f.read())

setup(name='tempodb-archive',
      version='1.0.0',
      description='Archive TempoDB Datapoints',
      long_description='\n\n'.join(long_descriptions),
      author='Emmanuel Levijarvi',
      author_email='emansl@gmail.com',
      url='https://github.com/eman/tempodb-archive',
      license='BSD',
      py_modules=['tempodb_archive'],
      install_requires=['tempodb'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Utilities',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='tempodb archive',
      entry_points={
          'console_scripts': ['tempodb-archive=tempodb_archive:main'],
      })
