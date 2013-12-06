#-*- coding: utf-8 -*-

# Copyright 2013 Juca Crispim <jucacrispim@gmail.com>

# This file is part of pyrocumulus.

# pyrocumulus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyrocumulus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pyrocumulus.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from tornado import ioloop
from importlib import import_module
from pyrocumulus.commands.base import BaseCommand


class RunTornadoCommand(BaseCommand):
    description = "command to start a tornado server"
    user_options = [
        # some.application.instance
        {'args': ('application',),
         'kwargs': {'help': 'application module'}},
        # --daemonize
        {'args': ('--daemonize',),
         'kwargs': {'default': False, 'help': 'run as a daemon',
                    'action': 'store_true'}},
        # --port=9876
        {'args': ('--port',),
         'kwargs': {'default': 8888, 'help': 'port to listen'}},
        # --stdout=some/file.log
        {'args': ('--stdout',),
         'kwargs': {'default': 'logs/stdout.log', 'help': 'stdout log file'}},
        # --stderr=some/file.log
        {'args': ('--stderr',),
         'kwargs': {'default': 'logs/stderr.log', 'help': 'stderr log file'}},
        # --pidfile=some/file.pid
        {'args': ('--pidfile',),
         'kwargs': {'default': None, 'help': 'stderr log file'}},
        # --kill
        {'args': ('--kill',),
         'kwargs': {'default': False, 'help': 'kill tornado server',
                    'action': 'store_true'}},
    ]
        

    def run(self):
        self.application = self._get_application(self.application)
        self.port = int(self.port)
        self.pidfile = self.pidfile or 'tornado-%i.pid' % self.port

        if self.kill:
            return self.killtornado()

        print('Starting tornado server')
        self.application.listen(self.port)
        if self.daemonize:
            self.run_as_a_daemon()
            self.close_file_descriptors()
            self.redirect_stdout_stderr()
            self._write_to_file(self.pidfile, str(os.getpid()))

        ioloop.IOLoop.instance().start()

    def killtornado(self):
        """
        Kills tornado server if pidfile is found
        """
        pid = None
        try:
            pid = int(self._read_file(self.pidfile))
        except IOError:
            print('Tornado pid file not found. Exiting')
        except TypeError:
            print('Bad content on pid file. Exiting')

        if pid is None:
            return False

        os.kill(pid, 9)
        print('Tornado server killed')
        os.remove(self.pidfile)
        return True

    def run_as_a_daemon(self):
        """
        Fork twice and setsid
        """
        self._do_fork()
        os.setsid()
        self._do_fork()

    def close_file_descriptors(self):
        """
        Closes stdin
        """
        # the `canonical` way of doing this is to close
        # all file descriptors, using RLIMIT_NOFILE.
        # But doing it here, crashes tornado server.
        sys.stdin.close()

    def redirect_stdout_stderr(self):
        """
        Redirect stdout and stderr to /dev/null or to a
        log file
        """
        for fd in sys.stdout, sys.stderr:
            fd.flush()

        stdout_fh = open(self.stdout, 'a', 1)
        stderr_fh = open(self.stderr, 'a', 1)
        os.dup2(stdout_fh.fileno(), sys.stdout.fileno())
        os.dup2(stderr_fh.fileno(), sys.stderr.fileno())

    def _try_create_required_dirs_and_files(self):
        dirs = []
        dirs.append(os.path.dirname(self.stdout))
        dirs.append(os.path.dirname(self.stderr))

        for directory in dirs:
            try:
                os.mkdir(directory)
            except OSError:
                pass

    def _do_fork(self):
        pid = os.fork()
        if pid != 0:
            sys.exit(0)

    def _read_file(self, fname):
        with open(fname) as f:
            content = f.read()
        return content

    def _write_to_file(self, fname, content):
        with open(fname, 'w') as f:
            f.write(content)

    def _get_application(self, app_path):
        module_name = '.'.join(app_path.split('.')[:-1])
        app_name = app_path.split('.')[-1]
        module = import_module(module_name)
        app = getattr(module, app_name)
        return app
