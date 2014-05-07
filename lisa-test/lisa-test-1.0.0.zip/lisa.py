"""
lisa's first example
"""
def print_lof(movies):
	for each_item in movies:
		if(isinstance(each_item, list)):
			print_lof(each_item)
		else:
			print(each_item)