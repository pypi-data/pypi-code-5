
"""printing element of list"""
def print_lol(aList):
	"""showme!"""

	for each_item in aList:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)