
from setuptools import setup, find_packages

setup(name='gse',
      version='0.1.9',
      description='extract metadata and dataset from GEO Series Matrix format data',
      author='Nick Seidenman',
      author_email='seidenman@wehi.edu.au',
      keywords='dataset extraction metadata GSE bioinformatics',
      packages=find_packages(),
      url='http://pypi.python.org/pypi/gse/',
      zip_safe=True,
      #scripts=['gse.py'],
      entry_points={'console_scripts': ['gse = gse.__main__:main', 
                                        'gse-guide = gse.guide:main',
                                        'gse-magma = gse.magma2:main', ] },
      install_requires=['python>=2.7', 'cfgparse>=1.3', 'pandas>=0.11', 'numpy>=1.7', 'matricks>=0.3' ],
      long_description=str(open('README.txt', 'r').read()),
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Topic :: Scientific/Engineering :: Bio-Informatics',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'License :: OSI Approved :: BSD License' ],
      )

