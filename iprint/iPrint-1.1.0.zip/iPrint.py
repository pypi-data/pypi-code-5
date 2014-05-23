""" iPrint: v1.0.0 
		Print funcitons
		Author: Sha Yi-Ming
"""

def print_me (a_list):
	print_me_level (a_list, -1)

def print_me_level (a_list, level):
	"""	Print an item
	if the item is a list, print each item of the list
	if not, print the item itself. 
	"""
	if isinstance (a_list, list):
		for item in a_list:
			print_me_level (item, level+1)
	else:
		for i in range (level):
			print ("\t", end='')
		print (a_list)

