# -*- coding: utf-8 -*-

import os, pkgutil, sys, inspect

def autoxinit(fullpkgname, initfilepath, _g, filter=None,
		import_modules=True,
		import_classes=True,
		import_functions=True ):

	if os.sep+'__init__.py' not in initfilepath: raise Exception, "'"+initfilepath+"' not an __init__ file"
	pkgpath=os.path.dirname(initfilepath)
	pkgcontents=[x for x in pkgutil.iter_modules([pkgpath])]

	if filter is not None: pkgcontents=filter(pkgcontents)


	modulefiles=[x[1] for x in pkgcontents]

	if import_modules:
		for loader, modulename, ispkg in pkgcontents:
			fullpkgname2=fullpkgname+'.'+modulename
			if fullpkgname2 in sys.modules:
				module=sys.modules[fullpkgname2]
			else:
				module=loader.find_module(fullpkgname2).load_module(fullpkgname2)
			_g[modulename]=module
			##################################
			#this wont be found in automodinit:
			if not ispkg: #only list contents of modules
				for (cond, isobj) in ((import_classes, inspect.isclass), (import_functions,inspect.isfunction)):
					if cond:
						for name, obj in inspect.getmembers(module, isobj):
							_g[name]=obj
							if name not in modulefiles:
								modulefiles.append(name)
			

	# this part is moved for also handling the imported classes and functions
	################################
	# Rewrite myself with the updated list

	if _g['__all__']!=modulefiles:
		initfilepath2=initfilepath[:-1] if initfilepath[-3:]!='.py' else initfilepath
		if os.path.exists(initfilepath2):
			# This may fail if running inside a ZIP file
			badmagic=False
			try:
				with open(initfilepath2, 'rU+') as meh:
					myself=meh.read()
					insertpoint=myself.find("# Don't modify the line above, or this line!")
					if insertpoint==-1:
						badmagic=True
						raise Exception, "Calling file missing magic modify line"
					newmyself='__all__ = '+repr(modulefiles)+'\n'
					newmyself+=myself[insertpoint:]
					meh.seek(0)
					meh.write(newmyself)
					meh.truncate()
			except:
				if badmagic: raise
		# Fix myself up to have the correct __all__
		_g['__all__']=modulefiles
