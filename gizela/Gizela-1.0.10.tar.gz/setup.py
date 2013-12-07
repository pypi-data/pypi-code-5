from distutils.core import setup

setup(
    name='Gizela',
    version='1.0.10',
    author='Michal Seidl, Tomas Kubin',
    author_email='michal.seidl@fsv.cvut.cz, tomas.kubin@fsv.cvut.cz',
    packages=['gizela',
              'gizela.data',
              'gizela.stat',
              'gizela.text',
              'gizela.util',
              'gizela.xml',
              'gizela.pyplot',
              'gizela.tran',
              'gizela.corr',
              'gizela.test'],
    package_dir={'gizela': 'gizela'},
    package_data={'docs': ['docs']},
    data_files=[('gizela/docs', ['../docs/*']),
                ('gizela/docs/examples', ['../docs/examples/*'])],
    scripts=['bin/gama-data-obs.py', 'bin/gama-data-adj.py', 'bin/coord2gamaObs.py'],
    url='http://geo.fsv.cvut.cz/gwiki/Gizela',
    license='LICENSE.txt',
    description='managing of geodetic networks, statistical tests of point displacement',
    long_description=open('README.txt').read(),
)
