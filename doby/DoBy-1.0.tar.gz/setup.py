from distutils.core import setup

long_description = '''
DoBy is a python module for creating TODOs in your code.
DoBy will raise an exception if the date passed into the
TODO function is greater than the current system time.
'''

setup(
    name='DoBy',
    version='1.0',
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    packages=['do_by', 'tests'],
    url='http://pypi.python.org/pypi/DoBy/',
    license='LICENSE',
    description='Time based TODOs.',
    long_description=long_description
)
