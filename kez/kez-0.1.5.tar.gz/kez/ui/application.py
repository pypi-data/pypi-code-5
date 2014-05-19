
import os
import logging
import sys
import inspect
import shlex

from cliff.app import App
from cliff.command import Command
from cliff.lister import Lister
from cliff.commandmanager import CommandManager, EntryPointWrapper

from kez import __version__
from kez.utils import import_object

pathjoin = os.path.join
expanduser = os.path.expanduser

def get_default_data_path():
    try:
        return os.environ["KEZ_DATA_PATH"]
    except KeyError:
        return pathjoin(expanduser("~"), ".kez", "data.db")

def iscommandclass(obj):
    return obj is not Command \
            and obj is not Lister \
            and inspect.isclass(obj) \
            and not inspect.isabstract(obj) \
            and hasattr(obj, '__dict__') \
            and 'take_action' in obj.__dict__

def commands_from_module(m, subcommand=True):
    if subcommand:
        prefix = m.rpartition('.')[2] + ' '
    else:
        prefix = ''
    m = import_object(m)
    d = {}
    for k, v in m.__dict__.items():
        if iscommandclass(v):
            d[(prefix + k).strip('_').lower()] = EntryPointWrapper(k.lower(), v)
    return d

class UICommandManager(CommandManager):

    def _load_commands(self):
        self.commands.update(commands_from_module('kez.ui.commands.base', False))

    def find_command(self, argv):
        try:
            return super(UICommandManager, self).find_command(argv)
        except ValueError as err:
            if str(err).startswith("Unknown command "):
                raise ValueError("unknown command '%s'" % ' '.join(argv))
            raise

class UI(App):
    NAME = "kez"
    log = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(
            description='Static Document Builder.',
            version=__version__,
            command_manager=UICommandManager('kez.ui'),
            )
        )
        super(UI, self).__init__(*args, **kwargs)

    def build_option_parser(self, description, version):
        parser = super(UI, self).build_option_parser(description, version)
        parser.add_argument(
            '-d',
            '--data-path',
            action='store',
            dest='data_path',
            default=get_default_data_path(),
            help="the path to an sqlite database (defaults to '~/.kez/data.db')",
        )
        return parser

    def interact(self):
        return self.run(['-h'])

def main(argv=sys.argv[1:]):
    try:
        ui = UI()
        ui.run(argv)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        if '--debug' in argv:
            raise
        else:
            sys.stderr.write("%s\n" % str(e))
            sys.exit(1)
        
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

