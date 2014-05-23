""" iPrint: v1.0.0 
		Print funcitons
		Author: Sha Yi-Ming
"""

def print_me (a_list):
	"""	Print an item
	if the item is a list, print each item of the list
	if not, print the item itself. 
	"""
	if isinstance (a_list, list):
		for item in a_list:
			print_me (item)
	else:
		print (a_list)

