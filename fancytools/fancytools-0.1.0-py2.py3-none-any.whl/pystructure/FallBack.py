# -*- coding: utf-8 -*-

import sys


class FallBack(object):
	'''
	a class allowing to automatially using another module as fallback
	if the given module doesn't have a needed attribute
	
	to create the fallback compatibitily just ad the folowing line to your module:
	
	FallBack(__name__, MyFallBackModule, print_warning=True)
	
	'''

	def __init__(self, ownModuleName, fallbackModule, print_warning=True):
		
		self.wrappedModule = sys.modules[ownModuleName]
		self.fallbackModule = fallbackModule
		self.print_warning = print_warning
		#register Fallback-wrapper in sys:
		sys.modules[ownModuleName] = self


	def __getattr__(self, name):
		try:
			return getattr(self.wrappedModule, name)
		except AttributeError:
			if self.print_warning:
				print 'WARING: no %s class exists for %s yet ... continue using fallback' %(
					self.wrappedModule.__name__,name)
			return getattr(self.fallbackModule, name)