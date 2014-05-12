# -*- coding: utf-8 -*-
from numpy import linspace as _linspace

def linspace2(a, b, n):
	'''exclude the boundayries'''
	###very unclean ...
	###only usable for linear increase
	a = _linspace(a, b, n+1)[:-1]
	#a.pop(-1)
	if len(a) > 1:
		diff01 = (a[1]-a[0])/2
		for i in range(len(a)):
			a[i] += diff01
	return a
