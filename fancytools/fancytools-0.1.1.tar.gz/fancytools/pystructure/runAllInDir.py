# -*- coding: utf-8 -*-

import pkgutil
import runpy
import os

def runAllInDir(dir_path):
	#pkgpath = os.path.abspath(os.curdir)
	pkgname = os.path.split(dir_path)[-1]
	thismodname = '%s.%s' %(pkgname, os.path.split(__file__)[-1][:-3])

	print 'testing all modules of %s' %dir_path
	for importer, modname, ispkg in pkgutil.walk_packages(
			[dir_path],
			onerror=lambda x: None):
		if not ispkg and modname != thismodname:#dont test this module
			print '... %s' %modname
			#module = importer.find_module(modname).load_module(modname)
			runpy.run_module(modname, init_globals=None, run_name='__main__', alter_sys=False)
	