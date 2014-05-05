#!/usr/bin/python

class Version:
	def __init__(self, ver_str):
		'''
		>>> v = Version('1.2.3')
		>>> v.major_ver, v.minor_ver, v.bugfix_number
		(1, 2, 3)
		>>> v = Version('1.2')
		>>> v.major_ver, v.minor_ver, v.bugfix_number
		(1, 2, None)
		'''
		v = map(int, ver_str.split('.'))
		v = v + [None] * (3 - len(v))
		self.major_ver, self.minor_ver, self.bugfix_number = v
