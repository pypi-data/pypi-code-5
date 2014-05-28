#!/usr/bin/env python
"""
"""
# Python 2.6 and newer support
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (
                bytes, dict, int, list, object, range, str,
                ascii, chr, hex, input, next, oct, open,
                pow, round, super,
                filter, map, zip)
try:
    unicode()
except NameError:
    unicode = str

import sys
__python_version__ = dict()
try:
    __python_version__['major'] = sys.version_info.major
except AttributeError:
    __python_version__['major'] = sys.version_info[0]
try:
    __python_version__['minor'] = sys.version_info.minor
except AttributeError:
    __python_version__['minor'] = sys.version_info[1]

import time
import argparse  # included in Python >2.7

try:
    import configparser  # Python 3.x
except ImportError:
    import ConfigParser as configparser  # Python 2.x

import logging
import logging.handlers
import traceback
import inspect

if __python_version__['major'] > 2:
    from io import StringIO
else:
    from StringIO import StringIO as StringIO2x
    class StringIO(StringIO2x):
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

from xml.sax import saxutils
from collections import defaultdict

from .dictattraccessor import DictAttrAccessor


class ApplicationConfig(configparser.ConfigParser):
    """
    """
    def __init__(self, file_path):
        configparser.ConfigParser.__init__(self)
        self._file_path = file_path
        if file_path is not None:
            self.read(file_path)

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    def __str__(self):
        return 'ApplicationConfig("{path}")'.format(path=self._file_path)

    def __repr__(self):
        return self.__str__()


class BasicArgumentParser(argparse.ArgumentParser):
    """
    """
    def __init__(self, default_config_file=None, **kwargs):
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                          help='output additional information to stderr (more v\'s mean more output, 4 is maximal)')
        # Only enable the config option is the default config is not set to None.
        if default_config_file is not None:
            self.add_argument('--config', dest='config', action='store',
                              default=default_config_file, type=ApplicationConfig,
                              help='path to the configuration file.')
        self.add_argument('--netlog-host', dest='netlog_host', action='store',
                          default=None, type=str,
                          help='hostname of the socket server to which log events will be sent (e.g., "localhost")')
        self.add_argument('--netlog-port', dest='netlog_port', action='store',
                          default=logging.handlers.DEFAULT_TCP_LOGGING_PORT, type=int,
                          help='port number of the socket logging handler to which log events will be sent')


class LogAboveErrorFilter(logging.Filter):
    """
    """
    def __init__(self):
        logging.Filter.__init__(self)

    def filter(self, record):
        # CRITICAL = 50
        # ERROR = 40
        # WARNING = 30
        # INFO = 20
        # DEBUG = 10
        # NOTSET = 0
        if record.levelno < logging.ERROR:
            return 1
        else:
            return 0


class Application(object):
    """
    """
    STDLOG_FSPEC = '[pid: %(process)d | log: %(name)s | level: %(levelname)s | time: %(asctime)s]\n\t>>> %(message)s'
    STDERR_FSPEC = STDLOG_FSPEC

    def __init__(self, name='', version='0.1.0', description='', epilog='', default_config_file=None,
                 stdout=sys.stdout, stderr=sys.stderr, stdlog=sys.stderr, credits=None, organization=''):
        object.__init__(self)
        self.name = name

        self.app_debug_id = None
        self._stdlog_handler = None
        self._stderr_handler = None
        self._netlog_handler = None

        self.version = version
        self.full_name = '{n}, version {v}'.format(n=name, v=version)
        self.description = description
        self.epilog = epilog
        self.organization = organization
        self.credits = credits
        self.stdout = stdout
        self.stderr = stderr
        self.stdlog = stdlog

        self.args = None
        self.config = None
        self.log = None

        self.state = DictAttrAccessor(dict_=defaultdict(lambda: None))  # dict with default type of None (2.x & 3.x)

        # argument parser
        self._arg_parser = BasicArgumentParser(default_config_file=default_config_file,
                                               prog=name,
                                               description=description,
                                               epilog=epilog,
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                               fromfile_prefix_chars='@')
        self._arg_parser.add_argument(
            '--version', action='version', version='%(prog)s {vers}'.format(vers=self.version))

    @property
    def id_(self):
        organization = self.organization.lower().strip().replace('.', '-').replace(' ', '_')
        name = self.name.lower().strip().replace('.', '-').replace(' ', '_')
        version = self.version.lower().strip().replace('.', '-').replace(' ', '_')
        return '{org}.{name}.{vers}'.format(org=organization, name=name, vers=version)

    def print(self, *args, **kwargs):
        if 'file' in kwargs:
            return print(*args, **kwargs)
        else:
            return print(*args, file=self.stdout, **kwargs)

    def add_argument(self, name, help_='', type_=str, nargs=1):
        safe_name = "".join(name.split())
        self._arg_parser.add_argument(
            safe_name, metavar=safe_name.upper(), type=type_, nargs=nargs,
            help=help_)

    def add_option(self, name, default=None, help_='',  type_=str, dest=None):
        if default is None:
            default = type_()

        safe_name = "".join(name.split())
        if dest is None:
            dest = safe_name

        optname = safe_name.lower().replace('_', '-')
        self._arg_parser.add_argument(
            '--{n}'.format(n=optname), dest=dest, action='append',
            default=[default], type=type_,
            help=help_)

    def _initialize(self):
        pass

    def _main(self, *args, **kwargs):
        pass

    def _on_success(self):
        pass

    def _on_failure(self):
        pass

    def _finalize(self):
        pass

    def exec_(self, *args, **kwargs):
        self.run(*args, **kwargs)

    def run(self, args=[], **kwargs):
        self.app_debug_id = '{c}.{f}'.format(c=str(self.__class__).strip().split("'")[1],
                                             f=inspect.currentframe().f_code.co_name)

        # initialize the application based on given arguments.
        self.args = self._arg_parser.parse_args(args)
        self.config = self.args.config if hasattr(self.args, 'config') else ApplicationConfig(file_path=None)
        assert hasattr(self.args, 'verbose')

        # logging facility
        self.log = logging.getLogger(self.id_)

        assert self.log is not None
        assert hasattr(self.log, 'critical')
        assert hasattr(self.log, 'error')
        assert hasattr(self.log, 'warning')
        assert hasattr(self.log, 'info')
        assert hasattr(self.log, 'debug')

        logging_level = logging.ERROR
        if self.args.verbose == 1:
            logging_level = logging.WARNING
        elif self.args.verbose == 2:
            logging_level = logging.INFO
        elif self.args.verbose > 2:
            logging_level = logging.DEBUG

        self.log.setLevel(logging_level)

        if self.stdlog is not None:
            # events with a level above that of ERROR
            self._stdlog_handler = logging.StreamHandler(self.stdlog)
            stdlog_formatter = logging.Formatter(self.STDLOG_FSPEC)
            self._stdlog_handler.setFormatter(stdlog_formatter)
            self._stdlog_handler.addFilter(LogAboveErrorFilter())
            self.log.addHandler(self._stdlog_handler)

        if self.args.netlog_host and self.args.netlog_port:
            # a network capable logging facility (remote possibilities, etc.)
            self._netlog_handler = logging.handlers.SocketHandler(self.args.netlog_host, self.args.netlog_port)
            self.log.addHandler(self._netlog_handler)

        if self.stderr is not None:
            # events with a level of ERROR and below
            self._stderr_handler = logging.StreamHandler(self.stderr)
            stderr_formatter = logging.Formatter(self.STDERR_FSPEC)
            self._stderr_handler.setFormatter(stderr_formatter)
            self._stderr_handler.setLevel(logging.ERROR)
            self.log.addHandler(self._stderr_handler)

        # ready to roll!
        self.log.debug('Entering {app_id}'.format(app_id=self.app_debug_id))
        try:
            assert self.config is not None
            assert self.args is not None

            self.log.debug('config = {0!s}'.format(self.config.as_dict()))
            self.log.debug('args = {0!s}'.format(vars(self.args)))
            self.log.debug('log_name = "{0!s}"'.format(self.log.name))

            self.log.info('Executing initialization hook.')
            self._initialize()
            self.log.info('Executing primary function.')
            self._main(**kwargs)
            self.log.info('Primary function exited cleanly. Executing success hook.')

        except Exception as e:
            self.log.info('An exception occurred! Executing failure hook.')
            self._on_failure()
            with StringIO() as err_msg:
                print(e, file=err_msg)
                traceback.print_exc(file=err_msg)
                self.log.critical(err_msg.getvalue())
        else:
            self._on_success()
        finally:
            self.log.info('Executing finalization hook.')
            self._finalize()
            self.log.debug('Exiting {app_id}'.format(app_id=self.app_debug_id))

            # tear-down the logging facility
            if hasattr(self, '_stdlog_handler') and self._stdlog_handler is not None:
                self.log.removeHandler(self._stdlog_handler)

            if hasattr(self, '_stderr_handler') and self._stderr_handler is not None:
                self.log.removeHandler(self._stderr_handler)

            if hasattr(self, '_netlog_handler') and self._netlog_handler is not None:
                self.log.removeHandler(self._netlog_handler)

