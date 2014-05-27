"""This is a module which provides a function called print_list().This
function is can print the list."""
def print_list (alist , level=0):
	"""This function has two parametes,alist and level.alist is a python list,while level is a int number"""
	for each_item in alist :
		if isinstance( each_item,list):
			print_list(each_item,level+1)
		else :
			for tab_stop in range(level):
				print "\t",
			print (each_item)
