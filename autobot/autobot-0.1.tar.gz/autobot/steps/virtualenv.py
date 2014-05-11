"""
steps related to virtualenvs
"""

from buildbot.process.properties import WithProperties
from buildbot.steps.shell import ShellCommand  

class CreateVirtualenv(ShellCommand):
  """create a virtualenv"""
  # XXX needs to have virtualenv installed (on the slave)

  def __init__(self, directory, **kw):
    ShellCommand.__init__(self, **kw)
    self.addFactoryArguments(directory=directory)
    self.command = ['virtualenv', WithProperties(directory)]
