def print_list(the_list, indent = False, level=0):
	for lev1_item in the_list:
		if isinstance(lev1_item, list): 
			print_list(lev1_item, level +1)
		else:
                        if indent :
                                for num in range(level):
                                        print("\t", end=" ")
                                print(lev1_item)

                                

