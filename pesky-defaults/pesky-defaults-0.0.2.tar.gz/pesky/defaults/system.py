# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import platform

def system_defaults():
    system = platform.system().lower()
    if system == 'linux':
        return {
            'PREFIX': '/usr',
            'BIN_DIR': '/usr/bin',
            'SBIN_DIR': '/usr/sbin',
            'LIB_DIR': '/usr/lib',
            'LIBEXEC_DIR': '/usr/libexec',
            'SYSCONF_DIR': '/etc',
            'LOCALSTATE_DIR': '/var/lib',
            'RUN_DIR': '/var/run',
            'DATA_DIR': '/usr/share',
        }
    elif system == 'darwin':
        return {
            'PREFIX': '/usr',
            'BIN_DIR': '/usr/bin',
            'SBIN_DIR': '/usr/sbin',
            'LIB_DIR': '/usr/lib',
            'LIBEXEC_DIR': '/usr/libexec',
            'SYSCONF_DIR': '/etc',
            'LOCALSTATE_DIR': '/var/lib',
            'RUN_DIR': '/var/run',
            'DATA_DIR': '/usr/share',
        }
    elif system == 'windows':
        return dict()
    else:
        return dict()
