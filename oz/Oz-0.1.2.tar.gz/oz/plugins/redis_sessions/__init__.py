from __future__ import absolute_import, division, print_function, with_statement, unicode_literals

import os
import binascii
import hashlib
import oz.app

from .middleware import *
from .options import *
from .tests import *

def random_hex(length):
    """Generates a random hex string"""
    return binascii.hexlify(os.urandom(length))[length:]

def password_hash(password, password_salt=None):
    """Hashes a specified password"""
    password_salt = password_salt or oz.app.settings["session_salt"]
    salted_password = "".join([unicode(password_salt), password])
    return "sha256!%s" % unicode(hashlib.sha256(salted_password.encode("utf-8")).hexdigest())
