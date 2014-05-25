def print_list(the_list):
	for lev1_item in the_list:
		if isinstance(lev1_item, list): 
			print_list(lev1_item)
		else:
			print(lev1_item)

