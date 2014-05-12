# -*- coding: utf-8 -*-
import os
try:
	import pwd
except ImportError:
	import getpass
	pwd = None

def userName():
	if pwd:
		return pwd.getpwuid(os.geteuid()).pw_name
	else:
		return getpass.getuser()