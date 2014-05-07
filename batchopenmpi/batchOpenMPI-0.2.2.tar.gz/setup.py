from distutils.core import setup

setup(name='batchOpenMPI',
      description='Easy parallelization built on top of mpi4py.',
      long_description='Easy to get started with parallelization using openMPI. batchOpenMPI is built on top of the mpi4py python package, and offers a few basic but useful features.',
      version='0.2.2',
      py_modules=['batchOpenMPI',],
      author="Antoine Dymond",
      author_email="antoine.dymond@gmail.com",
      url="https://github.com/hamish2014/optTune/",
      license="MIT",
      classifiers = [  #taken from http://pypi.python.org/pypi?:action=list_classifiers
        "Development Status :: 3 - Alpha", 
        ],
      install_requires=[
          'numpy',
          'mpi4py',
          ]
      )
