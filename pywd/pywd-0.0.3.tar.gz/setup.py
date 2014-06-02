from pywd import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

dependencies = ['docopt']

setup(
    name='pywd',
    version='.'.join(str(x) for x in __version__),
    description='Command-line Python password generator',
    url='http://www.github.com/zafia/pywd',
    license='MIT License',
    author='Safia Abdalla',
    author_email='seabdalla@gmail.com',
    install_requires=dependencies,
    packages=['pywd',],
    entry_points={
        'console_scripts': ['pywd=pywd.pywd:generate'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
)
