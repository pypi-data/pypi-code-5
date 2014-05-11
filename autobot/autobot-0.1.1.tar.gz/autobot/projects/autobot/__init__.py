from autobot.process.factory import PythonSourceFactory
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shell import WithProperties

class TestAutobotFactory(PythonSourceFactory):
  """
  factory to test autobot
  """

  sources = {'hg': ['http://k0s.org/hg/autobot']}

  def __init__(self, platform=None, slaveport=7357, htmlport=7358, publichtmlport=7359, hg=None):

    # setup the environment
    PythonSourceFactory.__init__(self, platform=platform, name='autobot', hg=hg)

    # find the necessary scripts
    self.findScript('create-autobot')
    self.findScript('buildbot')
    self.findScript('buildslave')

    # make sure the template creator actually does something
    self.addStep(ShellCommand(command=[WithProperties('%(create-autobot)s'),
                                       '--list-factories'],
                              description='create-autobot --list-factories'))

    # make a master, slave pair
    self.addStep(ShellCommand(command=[WithProperties('%(create-autobot)s'),
                                       '-f', '-', # all factories,
                                       '--ircChannels', '', # no channels
                                       '--slaveport', str(slaveport),
                                       '--htmlport', str(htmlport),
                                       '--publichtmlport', str(publichtmlport),
                                       'bot'],
                              description="make an autobot",
                              workdir=WithProperties('%(virtualenv)s'),
                              haltOnFailure=True))


    # make sure they start
    self.addStep(ShellCommand(command=[WithProperties('%(buildbot)s'),
                                       'start', 'master'],
                              workdir=WithProperties('%(virtualenv)s/bot'),
                              description='start build master'))
    self.addStep(ShellCommand(command=[WithProperties('%(buildslave)s'),
                                       'start', 'slave'],
                              workdir=WithProperties('%(virtualenv)s/bot'),
                              description='start build slave'))


    # try to access the waterfall
    self.addStep(ShellCommand(command=['curl',
                                       'http://localhost:%s/' % htmlport]))

    # could try to actually build, but we won't here

    # stop them!
    self.addStep(ShellCommand(command=[WithProperties('%(buildbot)s'),
                                       'stop', 'master'],
                              workdir=WithProperties('%(virtualenv)s/bot'),
                              description='stop build master'))
    self.addStep(ShellCommand(command=[WithProperties('%(buildslave)s'),
                                       'stop', 'slave'],
                              workdir=WithProperties('%(virtualenv)s/bot'),
                              description='stop build slave'))
