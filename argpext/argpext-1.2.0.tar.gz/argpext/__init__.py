#!/usr/bin/env python

"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012,2014 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""

import sys
import time
import re
import os
import warnings
import inspect
import argparse
import collections

VERSION = (1,2,0)

from . import aux
from . import keywords
from . import debug
from . import tasks
from . import backward

from argpext.aux import ChDir
from argpext.keywords import KeyWords
from argpext.debug import FrameRef,chainref,DebugPrint
from argpext.tasks import display,make_hook,Task,Node,Main
from argpext.backward import Function,Unit,Categorical


__all__ = [

    # Global variable
    'VERSION',

    # aux
    'ChDir',

    # keywords
    'KeyWords',

    # debug
    'FrameRef','chainref','DebugPrint',

    # tasks
    'display','make_hook','Task','Node','Main',

    # backward
    'Function','Unit','Categorical'
    ]

