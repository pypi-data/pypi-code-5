from distutils.core import setup

long_description = '''
DoBy is a python module for creating TODOs in your code.
DoBy will raise an exception if the date or time passed
into the TODO function is before than the current time.
'''

setup(
    name='DoBy',
    version='1.0.2',
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    packages=['doby', 'tests'],
    url='http://pypi.python.org/pypi/DoBy/',
    license='LICENSE',
    description='Time based TODOs.',
    long_description=long_description
)
