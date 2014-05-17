#!/usr/bin/env python3

import os
import sys
import gettext

if sys.version_info.major != 3:
    raise Exception("Sorry this software only works with python 3.")

gettext.install('pypluzz', os.path.join(os.path.dirname(__file__),'i18n'))
