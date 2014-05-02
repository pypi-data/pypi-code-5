from distutils.core import setup

setup(
    name='ellingtonia',
    version='0.0.1',
    author='Song Jin',
    author_email='songjin@hotmail.com',
    packages=['bin'],
    scripts=['bin/dirfetcher.py'],
    # url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='ellingtonia, a documentation indexing tool',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "Flask == 0.10",
    ],
)