from setuptools import setup, find_packages
setup(
        name='pysickle',
        version='0.1.1',
        author='Janina Mass',
        author_email='janina.mass@hhu.de',
        packages=find_packages(),
        scripts=['pysickle/pysickle.py'],
        license='GPLv3',
        url='https://pypi.python.org/pypi/pysickle/',
        description='Remove outlier sequences from multiple sequence alignment',
        long_description=open('README.txt').read(),
        install_requires=['numpy', 'matplotlib'],
        classifiers=[
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
            ],
        )
