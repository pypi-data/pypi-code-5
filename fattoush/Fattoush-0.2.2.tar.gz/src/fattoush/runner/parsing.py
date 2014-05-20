# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
`parse_args` is the One True Place to see how the arguments passed in
at the command line translate to what is passed into the
FattoushConfigGroup, which in turn controls how everything else is run.
"""
import os
import argparse


def add_lettuce_group(parser):
    """
    :type parser: argparse.ArgumentParser
    """
    group = parser.add_argument_group('lettuce arguments')
    group.add_argument("-v", "--verbosity",
                       dest="verbosity",
                       default=4,
                       help='The verbosity level')

    group.add_argument("-s", "--scenarios",
                       dest="scenarios",
                       default=None,
                       help='Comma separated list of scenarios to run')

    group.add_argument("-t", "--tag",
                       dest="tags",
                       action='append',
                       default=[],
                       help='Tells lettuce to run the specified tags '
                            'only; can be used multiple times to '
                            'define more tags(prefixing tags with "-" '
                            'will exclude them and prefixing with "~" '
                            'will match approximate words)')

    group.add_argument("-r", "--random",
                       dest="random",
                       action="store_true",
                       default=False,
                       help="Run scenarios in a more random order to "
                            "avoid interference")

    group.add_argument("--with-xunit",
                       dest="enable_xunit",
                       action="store_true",
                       default=False,
                       help='Output JUnit XML test results to a file')

    group.add_argument("--xunit-file",
                       dest="xunit_file",
                       default=None,
                       type=str,
                       help='Write JUnit XML to this file. Defaults to'
                            ' lettucetests.xml')

    group.add_argument("--failfast",
                       dest="failfast",
                       default=False,
                       action="store_true",
                       help='Stop running in the first failure')

    group.add_argument("--pdb",
                       dest="auto_pdb",
                       default=False,
                       action="store_true",
                       help='Launches an interactive debugger upon '
                            'error')

    # Inspection assumes os.curdir is the project directory, in
    # practice it should be the working directory when fattoush is run.
    #noinspection PyUnresolvedReferences
    group.add_argument('base_path',
                       default=os.path.join(os.curdir, 'features'),
                       nargs='?')


def add_fattoush_group(parser):
    """
    :type parser: argparse.ArgumentParser
    """
    group = parser.add_argument_group('fattoush',
                                      'Arguments that affect how '
                                      'fattoush is run')
    group.add_argument('--parallel',
                       default=None,
                       choices=['webdriver'],
                       help='Use this to run multiple sets of tests '
                            'in parallel. Can specify to fork on '
                            '{%(choices)s}',
                       metavar='SPLIT_ON')

    group.add_argument('-c', '--config-file',
                       dest='config', action='store',
                       default=None, metavar='JSON_FILE_PATH',
                       help='Unless this is specified, the desired '
                            'webdriver configuration will be read '
                            'from the environment, for compatibility '
                            'with Teamcity\'s Sauce Labs Build '
                            'Feature functionality. '

                            'Given the path to a file fattoush will '
                            'read a json configuration.')

    printing = parser.add_mutually_exclusive_group()

    printing.add_argument('--ps', '--print-schema',
                          dest='print_schema', action='store_true',
                          help='Print to stdout the schema which '
                               'config files must adhere to.')

    printing.add_argument('--pc', '--print-example-config',
                          dest='print_config', action='store_true',
                          help='Print to stdout an example config file')


def parse_args(args):
    from ..config import VERSION
    parser = argparse.ArgumentParser(prog='fattoush')
    parser.add_argument('--version',
                        action='version',
                        version=VERSION)

    add_fattoush_group(parser)
    add_lettuce_group(parser)

    return parser.parse_args(args)