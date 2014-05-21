from setuptools import setup, find_packages
import os

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()
 
setup(
    name = 'TES-simulation',
    packages = find_packages(exclude=['tests*']),
    version = '0.1.0',
    license = 'GPL v3',
    description = 'Simulates a Token Exchange System (TES, a token--dollar local economy)',
    long_description=(read('README.rst') + '\n\n' +
                      read('HISTORY.rst')),
    author='John Boik',
    author_email='john.boik@PrincipledSocietiesProject.org',
    url='https://www.PrincipledSocietiesProject.org',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering'],
    install_requires=[],
    package_data={'tes-simulation': ['TES-simulation/data/INCTOT_2011_1yr.pickle']},
    include_package_data=True,   
)

 
