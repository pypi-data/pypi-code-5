from distutils.core import setup

setup(
    name='simple_mailbox',
    version='0.1.0',
    author='Jian, Gao',
    author_email='junglegao@gmail.com',
    packages=['mailbox'],
    scripts=[],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='imap utils can be used to get the latest email from specified sender.',
    long_description=open('README.md').read(),
)
