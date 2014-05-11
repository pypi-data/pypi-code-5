#!/usr/bin/env python

"""
MakeItSo templates for autobot

see http://k0s.org/hg/MakeItSo
"""

import os
import string
import sys
from makeitso.cli import MakeItSoCLI
from makeitso.template import assemble
from makeitso.template import MakeItSoTemplate
from makeitso.template import Variable
from projects import descriptions
from projects import factories
from StringIO import StringIO
from subprocess import check_call as call


def print_descriptions():
    """print factory descriptions"""

    buffer = StringIO()
    print >> buffer, 'Factories::\n'
    for key in sorted(factories.keys()):
        print >> buffer, '%s:' % key
        print >> buffer, descriptions[key].rstrip()
        print >> buffer
    return buffer.getvalue().strip()


class AutobotMasterTemplate(MakeItSoTemplate):
    name = 'autobot-master'
    description = 'template for the autobot buildbot master'
    templates = [os.path.join('template', 'master')]
    vars = [Variable('slave', 'buildslave name', 'slave'),
            Variable('os', 'buildslave os (win, mac, linux)', default='linux'),
            Variable('passwd', 'buildslave password', default='passwd'),
            Variable('slaveport', 'port to talk to slaves on', default=9010, cast=int),
            Variable('htmlport', 'port for waterfall display', default=8010, cast=int),
            Variable('publichtmlport', 'port for public waterfall display', default=8011, cast=int),
            Variable('botname', 'name of IRC bot', default='autobot'),
            Variable('ircHost', 'IRC host', default=''),
            Variable('ircChannels', 'channels for the IRC bot ("-" for none)', default='-'),
            Variable('domain', 'autobot domain name', default='localhost'),
            Variable('recipients', 'email recipients for all projects', '')
            ]

    def pre(self, variables, output):
        factory = variables.get('factories')
        if factory:
            assert(set(factory).issubset(factories.keys())), 'Factory must be one of: ' % ', '.join(factories.keys())
        elif self.interactive:
            print print_descriptions()
            sys.stdout.write('Enter factory: ')
            factory = raw_input()
            assert factory in factories, 'Factory must be one of: ' % ', '.join(factories.keys())
            variables['factories'] = [factory]
        else:
            raise AssertionError("No factory provided")

        # stringify for .ini file
        variables['factories'] = ' '.join([i for i in variables['factories']])

    def create(self, output, variables):
        command = ['buildbot', 'create-master', output]
        print ' '.join(command)
        call(command)

    def post(self, variables):
        """
        called after the template is applied
        """
        self.create(self.output, variables)


class AutobotSlaveTemplate(MakeItSoTemplate):
    name = 'autobot-slave'
    description = 'template for the autotools buildbot slave'
    templates = [os.path.join('template', 'slave')]
    vars = [Variable('master', 'host of the master', default='localhost'),
            Variable('slave', 'buildslave name', 'slave'),
            Variable('passwd', 'buildslave password', default='passwd'),
            Variable('slaveport', 'port to talk to slaves on', default=9010)]

    def create(self, output, variables):
        command = ['buildslave', 'create-slave', output,
                   '%s:%d' % (variables['master'], int(variables['slaveport'])),
                   variables['slave'],
                   variables['passwd'] ]
        print ' '.join(command)
        call(command)

    def post(self, variables, output):
        self.create(output, variables)


class AutobotTemplate(AutobotMasterTemplate, AutobotSlaveTemplate):
    name = 'autobot'
    description = 'template for the autotools buildbot master+slave'
    templates = ['template']
    vars = assemble(AutobotMasterTemplate, AutobotSlaveTemplate)
    vars.append(Variable('debug', 'whether to deploy in debug mode', default=True, cast='eval'))

    def post(self, variables, output):
        AutobotMasterTemplate.create(self, os.path.join(output, 'master'), variables)
        AutobotSlaveTemplate.create(self, os.path.join(output, 'slave'), variables)


class ProjectTemplate(MakeItSoTemplate):
    """
    template for creating new autobot project stubs for testing
    """
    name = 'autobot-project'
    templates = [os.path.join('projects', 'project.template')]
    vars = [Variable('description', 'description of the project'),
            Variable('repo', 'repository location of the project')]

# CLI front end class

class AutobotMasterCLI(MakeItSoCLI):
    """
    command line handler for the master
    """
    def parser(self):
        parser = MakeItSoCLI.parser(self)
        parser.add_option('-f', '--factory', dest='factories',
                          default=[], action='append',
                          help="factory to use ('--factory -' for all)")
        parser.add_option('--list-factories', dest='_list_factories',
                          default=False, action='store_true',
                          help="list available factories")
        return parser

    def parse(self, args=None, parser=None, options=None):

        # parse the command line
        if not parser or not options or not args:
            parser = self.parser()
            options, args = parser.parse_args()

        # list the factories
        if options._list_factories:
            print print_descriptions()
            parser.exit()

        # check for all factories
        if options.factories == ['-']:
            options.factories = factories.keys()

        # call the parent
        return MakeItSoCLI.parse(self, args, parser, options)


class ProjectTemplateCLI(MakeItSoCLI):
    """CLI front end for project template"""

    def __init__(self):
        self.usage = '%prog [options] project <output>'
        MakeItSoCLI.__init__(self, ProjectTemplate)

    def parse(self, args=None, parser=None, options=None):

        # parse the arguments
        parser = self.parser()
        options, args = parser.parse_args(args=args)
        if not(args):
            parser.print_usage()
            parser.exit()

        # deploy to the correct place
        if len(args) not in (1,2):
            parser.error("Please provide a single project")
        project = args[0].lower()

        # ensure the argument is a python path
        assert set(project).issubset(string.letters)

        # get the variables
        variables = self.get_variables(options)
        variables['project'] = project

        # get the output or use the location in the source
        if len(args) == 2:
            output = args[1]
        else:
            here = os.path.dirname(os.path.abspath(__file__))
            projectdir = os.path.join(here, 'projects', project)
            if os.path.exists(projectdir):
                assert os.path.isdir(projectdir)
            else:
                os.makedirs(projectdir)
            output = os.path.join(projectdir, '__init__.py')
            assert not os.path.exists(output), "Project '%s' already exists" % project

        return variables, output


### console_script front-ends

def create_master(args=sys.argv[1:]):
    cli = AutobotMasterCLI(AutobotMasterTemplate)
    cli(*args)

def create_slave(args=sys.argv[1:]):
    cli = MakeItSoCLI(AutobotSlaveTemplate)
    cli(*args)

def create_autobot(args=sys.argv[1:]):
    cli = AutobotMasterCLI(AutobotTemplate)
    cli(*args)

def create_project(args=sys.argv[1:]):
    cli = ProjectTemplateCLI()
    cli(*args)

if __name__ == '__main__':
    # default: create master
    create_master()
