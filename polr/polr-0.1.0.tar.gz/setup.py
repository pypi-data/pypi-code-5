from distutils.core import setup

setup(
    name='polr',
    version='0.1.0',
    author='Srijay C. Kasturi',
    author_email='srijay@techfilmer.com',
    packages=['polr'],
    url='http://polr.cf',
    license='LICENCE.txt',
    description='Polr Wrapper',
    long_description=open('README.txt').read(),
    install_requires=["requests>=2.2.1"]
)
