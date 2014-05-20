try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tcpy',
    packages=['tcpy'],
    version='0.0.8',
    url='https://github.com/pbrodie/tcpy',
    keywords=['TCP', 'server', 'client', 'framework'],
    classifiers=[],
    install_requires=['msgpack-python==0.4.2']
)
