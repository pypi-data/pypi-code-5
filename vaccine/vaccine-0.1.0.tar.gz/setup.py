from setuptools import setup, find_packages

def version(name):
  import os
  folder       = os.path.split(__file__)[0]
  version_file = os.path.join(folder, "{}/_version.py".format(name))
  env = {}
  execfile(version_file, env)
  return env['__version__']


if __name__ == '__main__':
  name = 'vaccine'
  setup(
    name         = name,
    version      = version(name),
    author       = 'Daniel Duckworth',
    author_email = 'duckworthd@gmail.com',
    description  = "A simple dependency injection framework",
    license      = 'BSD',
    keywords     = 'di dependency injection',
    url          = 'http://github.com/duckworthd/vaccine',
    packages     = find_packages(),
    classifiers  = [
      'Development Status :: 4 - Beta',
      'Programming Language :: Python',
    ],
    setup_requires   = [ 'setuptools>=3.4.4', ],
    install_requires = [],  # nothing!
    tests_require    = [ "nose" ],
    dependency_links = [],
    test_suite       = 'nose.collector',
  )
