"""Setup file for Student Evaluator

Define the options for the "student_evaluator" package
Create source Python packages (python setup.py sdist)
Create binary Python packages (python setup.py bdist)

"""
from distutils.core import setup

from student_evaluator import __version__


with open('README.txt') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(name='student_evaluator',
      version=__version__,
      description='Student Evaluator',
      long_description=LONG_DESCRIPTION,
      author='Jeroen Doggen',
      author_email='jeroendoggen@gmail.com',
      url='https://github.com/jeroendoggen/student-evaluator',
      packages=['student_evaluator'],
      package_data={'student_evaluator': ['*.py', '*.conf']},
      license='MIT',
      platforms=['Linux'],
      )
