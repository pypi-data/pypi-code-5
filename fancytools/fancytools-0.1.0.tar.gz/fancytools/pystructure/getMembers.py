# -*- coding: utf-8 -*-

import inspect

def getAvailableClassesInModule(prooveModule):
	'''
	return a list of all classes in the given module
	that dont begin with '_'
	'''
	l=tuple(x[1] for x in inspect.getmembers(prooveModule,inspect.isclass))
	l = [x for x in l if x.__name__[0] != "_" ]
	return l


def getAvailableClassesInPackage(package):
	'''
	return a list of all classes in the given package
	whose modules dont begin with '_'
	'''
	l=list(x[1] for x in inspect.getmembers(package,inspect.isclass))

	modules = list(x[1] for x in inspect.getmembers(package,inspect.ismodule))
	for m in modules:
		l.extend(list(x[1] for x in inspect.getmembers(m,inspect.isclass)))
	l = [x for x in l if x.__name__[0] != "_" ]
	n=0
	while n < len(l):
		cls =l[n]
		if not  cls.__module__.startswith(package.__name__):# in cls.__module__== package.__name__:# + '.' + cls.__module__:
			l.pop(n)
			n-=1
		n+=1
	return l


def getAvClassNamesInPackage(package):
	l = getAvailableClassesInPackage(package)
	return [x.__name__ for x in l]


def getAvClassNamesInModule(prooveModule):
	l = getAvailableClassesInModule(prooveModule)
	return [x.__name__ for x in l]


def getClassInPackageFromName(className, module):
	#TODO: more efficiency!
	n = getAvClassNamesInPackage(module)
	i = n.index(className)
	c = getAvailableClassesInPackage(module)
	return c[i]


def getClassInModuleFromName(className, module):
	n = getAvClassNamesInModule(module)
	i = n.index(className)
	c = getAvailableClassesInModule(module)
	return c[i]
