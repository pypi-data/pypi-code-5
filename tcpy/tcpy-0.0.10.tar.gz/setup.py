try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='tcpy',
    packages=['tcpy'],
    version='0.0.10',
    url='https://github.com/pbrodie/tcpy',
    description='Kitten-simple TCP Frameworks.',
    long_description='Because nobody has time to learn Twisted.\n\n' +
                     'Documentation: http://tcpy.readthedocs.org.\n\n' +
                     'Source hosted on Github: https://github.com/pbrodie/tcpy.',
    keywords=['TCP', 'server', 'client', 'framework'],
    classifiers=[],
    install_requires=['msgpack-python==0.4.2']
)
