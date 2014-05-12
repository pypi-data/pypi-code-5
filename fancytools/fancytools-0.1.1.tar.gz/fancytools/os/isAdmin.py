# -*- coding: utf-8 -*-
import ctypes, os


def isAdmin():
	try:
		is_admin = os.getuid() == 0
	except AttributeError:
		is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
	
	return is_admin