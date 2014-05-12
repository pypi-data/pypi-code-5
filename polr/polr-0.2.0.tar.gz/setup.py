from distutils.core import setup

setup(
    name='polr',
    version='0.2.0',
    author='Srijay C. Kasturi',
    author_email='srijay@techfilmer.com',
    packages=['polr'],
    url='http://polr.cf',
    license=open('LICENCE.txt').read(),
    description='Polr Wrapper',
    long_description=open('README.txt').read(),
    install_requires=["requests>=2.2.1"]
)
