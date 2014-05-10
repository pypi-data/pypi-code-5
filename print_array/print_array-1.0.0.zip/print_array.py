def print_lol (the_list):
	for z in the_list:
		if isinstance(z,list):
			print_lol(z)
		else:
			print (z)


			
