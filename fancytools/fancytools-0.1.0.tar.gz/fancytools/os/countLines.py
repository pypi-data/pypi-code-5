# -*- coding: utf-8 -*-

def countLines(filename):
	'''
	fast counting to the lines of a given filename
	through only reading out a limited buffer
	'''
	f = open(filename)
	try:
		lines = 1
		buf_size = 1024 * 1024
		read_f = f.read # loop optimization
		buf = read_f(buf_size)
		# Empty file
		if not buf:
			return 0
		while buf:
			lines += buf.count('\n')
			buf = read_f(buf_size)
		return lines
	finally:
		f.close()