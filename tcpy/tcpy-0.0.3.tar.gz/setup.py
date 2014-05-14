try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tcpy',
    packages=['tcpy'],
    version='0.0.3',
    description='Kitten-simple TCP Frameworks',
    url='https://github.com/pbrodie/tcpy',
    download_url='https://github.com/pbrodie/tcpy/tarball/0.0.3',
    keywords=['TCP', 'server', 'client', 'framework'],
    classifiers=[],
    install_requires=['msgpack-python==0.4.2']
)
