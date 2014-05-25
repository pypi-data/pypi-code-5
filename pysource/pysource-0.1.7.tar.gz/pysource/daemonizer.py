# Copyright 2014 Dan Kilman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import errno
import signal
import time

import daemon
import lockfile

from pysource import config, transport

STATUS_STOPPED = 'stopped'
STATUS_RUNNING = 'running'
STATUS_CORRUPTED = 'corrupted'

READ_PID_RETRY = -1

_pidfile_dir = lambda: config.pysource_dir
_pidfile_path = lambda: os.path.join(_pidfile_dir(), 'pidfile')
_pidfile = lambda: lockfile.FileLock(_pidfile_path())

_context = daemon.DaemonContext(
    pidfile=_pidfile(),
    stdout=sys.stdout,
    stderr=sys.stderr
)


def start():
    _make_pysource_dir()
    stat, _ = status()
    if stat == STATUS_CORRUPTED:
        _pidfile().break_lock()
        transport.cleanup()
    elif stat == STATUS_RUNNING:
        return False
    with _context:
        _write_pid()
        transport.start_server()


def stop(stat=None):
    stat, pid = stat or status()
    if stat != STATUS_RUNNING:
        return False
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError, e:
        if e.errno == errno.ESRCH:
            pass
        else:
            raise
    transport.cleanup()
    return True


def restart():
    stat, pid = status()
    if stat == STATUS_RUNNING:
        stop((stat, pid))
        time.sleep(1)
    start()


def status():
    stat = STATUS_STOPPED
    pid = None
    if _pidfile().is_locked():
        pid = _read_pid()
        if pid is None:
            if _pidfile().is_locked():
                return STATUS_CORRUPTED, pid
            else:
                return STATUS_STOPPED, pid
        if pid == READ_PID_RETRY:
            time.sleep(0.1)
            pid = _read_pid()
        stat = STATUS_RUNNING if _process_is_running(pid) else STATUS_CORRUPTED
    return stat, pid


def _write_pid():
    with open(_pidfile().lock_file, 'w') as f:
        f.write(str(os.getpid()))


def _read_pid():
    try:
        with open(_pidfile().lock_file, 'r') as f:
            return int(f.read())
    except IOError, e:
        if e.errno == errno.ENOENT:
            return None
        else:
            raise
    except ValueError:
        # it might be that status was called before the pid was actually
        # written to the file, so we'll return -1 to denote a retry
        # is in order
        return READ_PID_RETRY


def _make_pysource_dir():
    try:
        os.mkdir(_pidfile_dir())
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise


def _process_is_running(pid):
    try:
        os.kill(pid, signal.SIG_DFL)
    except OSError, e:
        return e.errno != errno.ESRCH
    else:
        return True
