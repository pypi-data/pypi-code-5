from uliweb.core.template import template

def test():
	"""
	>>> d = {'name':'guest'}
	>>> print template('Hello, {{=name}}', d)
	Hello, guest
	"""