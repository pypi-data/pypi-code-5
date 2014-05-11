from autobot.process.factory import PythonSourceFactory
from buildbot.steps.shell import ShellCommand
from buildbot.steps.shell import WithProperties

class TestToolbox(PythonSourceFactory):
    """
    an index of tagged tools
    """

    sources = {'hg': ['http://k0s.org/hg/toolbox'],}

    def __init__(self):
        PythonSourceFactory.__init__(self, name='toolbox')

        # run the tests
        self.addStep(ShellCommand(command=[WithProperties('%(python)s'), 'test.py'],
                                  workdir=WithProperties('%(virtualenv)s/src/toolbox/test'),
                                  description='test toolbox'))
