from distutils.core import setup

setup(
    name='boatd_client',
    version='0.1.4',
    author='Louis Taylor',
    author_email='kragniz@gmail.com',
    description=('Python wrapper for the boatd API, used to write behavior scripts.'),
    long_description=open("README.rst").read(),
    license='GPL',
    keywords='boat sailing wrapper rest',
    url='https://github.com/boatd/python-boatd',
    packages=['boatd_client'],
    requires=['docopt'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
