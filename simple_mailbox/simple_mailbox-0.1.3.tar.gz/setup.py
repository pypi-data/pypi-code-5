from distutils.core import setup

setup(
    name='simple_mailbox',
    version='0.1.3',
    author='Jian, Gao',
    author_email='junglegao@gmail.com',
    packages=['smbox'],
    scripts=[],
    url='https://pypi.python.org/pypi/simple_mailbox/',
    license='LICENSE.txt',
    description='imap utils can be used to get the latest email from specified sender.',
    long_description=open('README.txt').read(),
)
