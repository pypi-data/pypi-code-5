from distutils.core import setup

setup(
    name='Geoza',
    version='0.0.2',
    author='Tanner Baldus',
    author_email='tbaldus285@gmail.com',
    packages=['geoza'],
    scripts=[],
    url='http://pypi.python.org/pypi/geoza/',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='A prototype for playing songza playlists based on geoloction.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.2.1",
        "docopt >= 0.6.1",
    ],
    entry_points={
        'console_scripts': [
         'geoza = geoza.geoza:main',
        ],
        }
)