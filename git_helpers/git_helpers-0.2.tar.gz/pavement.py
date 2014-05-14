from paver.easy import task, needs
from paver.setuputils import setup

import version


setup(name='git_helpers',
      version=version.getVersion(),
      description='Wrapper API around `git` commands.',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/git_helpers.git',
      license='GPLv2',
      packages=['git_helpers'])


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
