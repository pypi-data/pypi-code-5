"""
generic factories for autobot
"""

from autobot.steps import CreateVirtualenv
from buildbot.process.factory import BuildFactory
from buildbot.steps.shell import SetProperty
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shell import WithProperties


### utility functions; could go elsewhere

def find(*args):
  """
  returns a command to echo the found file cross-platform
  """
  args = ['[ -e "%s" ]; then echo "${PWD}/%s"' % (arg, arg) for arg in args]
  command = 'if %s; else false; fi' % '; elif '.join(args)
  return ['bash', '-c', command]

### factories

class SourceFactory(BuildFactory):
  """
  base class for factories with VCS sources
  """

  sources = {'git': [], 'hg': []}
  default_branches = {'git': 'master', 'hg': 'default'}

  def __init__(self, git=None, hg=None):

    BuildFactory.__init__(self)

    # override class-level defaults
    if git is not None:
      self.sources['git'] = git
    if hg is not None:
      self.sources['hg'] = hg

    # sanitize sources
    for source_type in self.sources:
      if isinstance(self.sources[source_type], basestring):
        self.sources[source_type] = self.sources[source_type].split()
      for index, source in enumerate(self.sources[source_type]):
        if isinstance(source, basestring):
          branch = None
          if '#' in source:
            source, branch = source.rsplit('#', 1)
        else:
          source, branch = source
        if branch is None:
          branch = self.default_branches.get(source_type, None)
        self.sources[source_type][index] = (source, branch)

  def checkout(self, **kwargs):
    """
    checkout all sources
    """
    # TODO: do the right thing with branches (they're currently ignored)
    # TODO: should give more fine-grained control

    # clone hg repositories
    for hg_source, branch in self.sources.get('hg', ()):
      self.addStep(ShellCommand(command=['hg', 'clone', hg_source],
                                **kwargs))
      if branch and branch != 'default':
        dirname = self.dirname('hg', hg_source)
        self.addStep(ShellCommand(command=['hg', '-R', dirname, 'checkout', branch],
                                  **kwargs))

    # clone the git repositories
    for git_source, branch in self.sources.get('git', ()):
      self.addStep(ShellCommand(command=['git', 'clone', git_source],
                                **kwargs))
      if branch and branch != 'master':
        dirname = self.dirname('git', git_source)
        self.addStep(ShellCommand(command=['git', '--git-dir', dirname + '/.git',
                                           '--work-tree', dirname,
                                           'checkout', branch],
                                  **kwargs))

  def dirname(self, type, repo):
    """
    get the directory name for a given repo
    """
    if type == 'git':
      dirname = repo.rstrip('/').rsplit('/', 1)[-1]
      if dirname.endswith('.git'):
        dirname = dirname[:-4]
      return dirname
    elif type == 'hg':
      return repo.rstrip('/').rsplit('/')[-1]
    else:
      raise NotImplementedError("Unknown repository type: %s" % type)


class VirtualenvFactory(SourceFactory):
  """
  create a virtualenv and install some python packages in it
  """

  def __init__(self, name='env', hg=None, git=None, checkout=True):
    """
    - name : of the virtualenv
    - hg: sources of python packages with setuptools setup.pys
    - git: git sources of python package
    """
    SourceFactory.__init__(self, hg=hg, git=git)

    # wipe any vestiges
    self.addStep(ShellCommand(command=['rm', '-rf', name]))

    # create a virtualenv
    self.addStep(CreateVirtualenv(name))

    # set properities related to the virtualenv:
    # - virtualenv location
    # - scripts location
    # - python location
    self.addStep(SetProperty(property='virtualenv',
                             command=['pwd'],
                             workdir='build/'+name))
    self.addStep(SetProperty(property='scripts',
                             command=find('Scripts', 'bin'),
                             workdir=WithProperties('%(virtualenv)s')))
    self.findScript('python')

    # add a source directory
    self.addStep(ShellCommand(command=['mkdir', '-p', 'src'],
                              workdir=WithProperties('%(virtualenv)s')))

    # checkout sources
    if checkout:
      self.checkout(workdir=WithProperties('%(virtualenv)s/src'),
                    haltOnFailure=True)


  def findScript(self, script):
    """
    find the name of the script cross-platform
    - script: unix-style name of the script
    """
    self.addStep(SetProperty(property=script,
                             command=find(script, script + '.exe'),
                             workdir=WithProperties('%(scripts)s')))

  def addScripts(self):
    """
    add the scripts directory to the $PATH
    """
    self.addStep(SetProperty(property='PATH',
                             command=WithProperties('echo %(scripts)s:$PATH')))


class PythonSourceFactory(VirtualenvFactory):
  """
  setup several python packages
  """

  def __init__(self, platform=None, name='env', hg=None, git=None):

    # setup the environment
    VirtualenvFactory.__init__(self, name=name, hg=hg, git=git)

    # install the packages
    packages = []
    for hg_source, branch in self.sources.get('hg', ()):
      package = self.dirname('hg', hg_source)
      packages.append(package)
    for git_source, branch in self.sources.get('git', ()):
      package = self.dirname('git', git_source)
      packages.append(package)
    for package in packages:
      self.addStep(ShellCommand(command=[WithProperties('%(python)s'), 'setup.py', 'install'],
                                workdir=WithProperties('%(virtualenv)s/src/' + package),
                                description='install ' + package,
                                haltOnFailure=True))
