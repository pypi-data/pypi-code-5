#!/usr/bin/env python

"""
greplog.remote
~~~~~~~~~~~~~~

Handle remote connections.
Currently using fabric.

"""

from fabric.operations import run, sudo
from fabric.api import (
    env as fab_env,
    hide as fab_hide,
)

